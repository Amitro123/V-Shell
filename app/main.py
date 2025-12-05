import asyncio
import logging
import sys
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from app.config import load_config
from app.audio.recorder import AudioRecorder
from app.audio.stt import Transcriber
from app.audio.stt import Transcriber
from app.llm.router import Brain
from app.core.executor import GitExecutor
from app.core.models import GitTool
from app.core.metrics import MetricsLogger
from app.core.policies import TOOL_POLICIES, ToolPolicy

# Configure logging
logging.basicConfig(
    level=logging.WARNING, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gitvoice")

console = Console()

async def main():
    console.print(Panel.fit("[bold green]GitVoice[/bold green] - Hands-Free Git Assistant", border_style="green"))
    
    # Load config
    try:
        config = load_config()
        # Set log level from config
        logging.getLogger().setLevel(config.log_level)
    except Exception as e:
        console.print(f"[bold red]Configuration error:[/bold red] {e}")
        return
    
    # Initialize components
    with console.status("[bold green]Initializing components...[/bold green]"):
        try:
            recorder = AudioRecorder(config)
            transcriber = Transcriber(config)
            brain = Brain(config)
            executor = GitExecutor(config, brain, console=console)
            metrics_logger = MetricsLogger()
        except Exception as e:
            console.print(f"[bold red]Initialization failed:[/bold red] {e}")
            return

    console.print("[dim]Press Ctrl+C to exit[/dim]")
    
    async def run_tool_with_policy(tool_call: GitTool, raw_text: str):
        policy = TOOL_POLICIES.get(tool_call.tool.value, ToolPolicy(False, 0, []))
        
        # 1. Human Confirmation
        if policy.confirmation_required and config.require_confirmation_writes:
            console.print(f"[bold yellow]Safety Check:[/bold yellow] About to execute: {tool_call.tool.value} ({tool_call.params})")
            if not Confirm.ask(f"[bold red]Are you sure?[/bold red]"):
                console.print("[red]Cancelled by user.[/red]")
                metrics_logger.log(raw_text, tool_call.tool.value, success=False, error="cancelled_by_user")
                return

        # 2. Generic Retry
        attempts = policy.retries + 1
        for i in range(attempts):
            try:
                with console.status(f"[dim]Executing {tool_call.tool.value} (attempt {i+1}/{attempts})...[/dim]"):
                    start_time = asyncio.get_event_loop().time()
                    result = await executor.execute(tool_call)
                    end_time = asyncio.get_event_loop().time()
                    duration = (end_time - start_time) * 1000

                is_success = result.success
                should_retry = False
                
                if not is_success:
                    if result.exit_code in policy.retry_on_exit_codes:
                        should_retry = True
                
                metrics_logger.log(
                    raw_text, 
                    tool_call.tool.value, 
                    success=is_success, 
                    error=result.stderr if not is_success else None,
                    duration_ms=duration
                )

                if is_success:
                    console.print(Panel(result.stdout, title="[bold green]Success[/bold green]", border_style="green"))
                    return
                
                if should_retry and i < attempts - 1:
                    console.print(f"[yellow]Command failed with code {result.exit_code}. Retrying...[/yellow]")
                    await asyncio.sleep(0.5)
                    continue
                
                # Final failure
                console.print(Panel(result.stderr, title="[bold red]Error[/bold red]", border_style="red"))
                return

            except Exception as e:
                console.print(f"[bold red]Exception during execution:[/bold red] {e}")
                metrics_logger.log(raw_text, tool_call.tool.value, success=False, error=str(e))
                if i == attempts - 1:
                    return

    try:
        while True:
            console.print("\n[bold blue]Press Enter to START recording (or 'q' to quit)...[/bold blue]")
            cmd = input().strip().lower()
            if cmd == 'q':
                break
            
            # 1. Start Recording
            recorder.start_recording()
            
            # 2. Stop Recording
            console.print("[bold red]Recording... Press Enter to STOP.[/bold red]")
            input()
            audio_path = recorder.stop_recording()
            
            if not audio_path:
                console.print("[red]No audio captured.[/red]")
                continue

            console.print(f"[dim]Saved audio: {audio_path}[/dim]")
            
            # 2. Transcribe
            with console.status("[dim]Transcribing...[/dim]"):
                stt_result = await transcriber.transcribe(audio_path)
            
            if not stt_result.text:
                console.print("[red]Could not understand anything, please try again.[/red]")
                continue
                
            console.print(f"[bold]Heard:[/bold] \"{stt_result.text}\"")
            
            # 3. Brain
            with console.status("[dim]Thinking...[/dim]"):
                tool_call = await brain.process(stt_result.text)
            
            console.print(f"[dim]Planned action:[/dim] {tool_call.tool.value} ({tool_call.params})")
            
            if tool_call.tool == GitTool.HELP:
                console.print(f"[yellow]{tool_call.explanation}[/yellow]")
                continue
            
            # 4. Execute with Policy
            # Inject confirmation callback for smart commit (safe since in-process)
            if tool_call.tool == GitTool.SMART_COMMIT_PUSH:
                tool_call.params["confirm_callback"] = lambda msg: Confirm.ask(f"[bold yellow]{msg}[/bold yellow]")
                
            await run_tool_with_policy(tool_call, stt_result.text)
                    
    except KeyboardInterrupt:
        console.print("\n[bold blue]GitVoice stopping...[/bold blue]")
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in main loop")

if __name__ == "__main__":
    asyncio.run(main())
