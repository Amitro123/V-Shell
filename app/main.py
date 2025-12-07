import asyncio
import logging
import sys
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from app.config import load_config
from app.audio.recorder import AudioRecorder
from app.audio.stt import Transcriber
from app.audio.feedback import play_start_listening_sound, play_stop_listening_sound
from app.llm.router import Brain
from app.core.executor import execute_tool
from app.core.models import ToolCall
from app.core.metrics import MetricsLogger
from app.core.policies import TOOL_POLICIES, ToolPolicy
from app.cli.ui import (
    show_status,
    show_error,
    show_success,
    spinner,
    render_git_status,
    render_git_log,
    render_git_diff,
    render_test_results,
    render_smart_commit,
    render_simple_block,
)

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
            metrics_logger = MetricsLogger()
        except Exception as e:
            console.print(f"[bold red]Initialization failed:[/bold red] {e}")
            return

    console.print("[dim]Press Ctrl+C to exit[/dim]")
    
    async def run_tool_with_policy(tool_call: ToolCall, raw_text: str):
        # Handle string tool names by checking if they are in Enum or just defaulting
        policy = TOOL_POLICIES.get(tool_call.tool, ToolPolicy(False, 0, []))
        
        # 1. Human Confirmation
        if (policy.confirmation_required or tool_call.confirmation_required) and config.require_confirmation_writes:
            console.print(f"[bold yellow]Safety Check:[/bold yellow] About to execute: {tool_call.tool} ({tool_call.params})")
            if not Confirm.ask(f"[bold red]Are you sure?[/bold red]"):
                console.print("[red]Cancelled by user.[/red]")
                metrics_logger.log(raw_text, tool_call.tool, success=False, error="cancelled_by_user")
                return

        # 2. Generic Retry
        attempts = policy.retries + 1
        for i in range(attempts):
            try:
                start_time = asyncio.get_event_loop().time()
                
                # Call stateless executor with spinner
                with spinner(f"Executing {tool_call.tool}..."):
                    result_dict = await execute_tool(tool_call, config=config, brain=brain, console=console)
                
                end_time = asyncio.get_event_loop().time()
                duration = (end_time - start_time) * 1000

                is_success = result_dict.get("success", False) # execute_tool now returns dict
                exit_code = result_dict.get("exit_code", 0)
                stdout = result_dict.get("stdout", "")
                stderr = result_dict.get("stderr", "")
                
                should_retry = False
                
                if not is_success:
                    if exit_code in policy.retry_on_exit_codes:
                        should_retry = True
                
                metrics_logger.log(
                    raw_text, 
                    tool_call.tool, 
                    success=is_success, 
                    error=stderr if not is_success else None,
                    duration_ms=duration
                )

                if is_success:
                    # Render output based on tool type
                    tool = tool_call.tool
                    
                    if tool == "git.status":
                        render_git_status(stdout)
                    elif tool == "git.log":
                        render_git_log(stdout)
                    elif tool == "git.diff":
                        render_git_diff(stdout)
                    elif tool == "git.run_tests":
                        summary = result_dict.get("summary", "Test run finished")
                        render_test_results(summary, stdout)
                    elif tool == "git.smart_commit_push":
                        render_smart_commit(result_dict)
                    else:
                        # Generic rendering for other tools
                        render_simple_block(tool, stdout)
                    
                    show_success(f"✓ {tool} completed successfully")
                    return
                
                if should_retry and i < attempts - 1:
                    show_error(f"Command failed with code {exit_code}. Retrying...")
                    await asyncio.sleep(0.5)
                    continue
                
                # Final failure
                show_error(f"{tool_call.tool} failed with exit code {exit_code}")
                if stderr:
                    render_simple_block("Error Details", stderr, border_style="red")
                return

            except Exception as e:
                show_error(f"Exception during execution: {e}")
                metrics_logger.log(raw_text, tool_call.tool, success=False, error=str(e))
                if i == attempts - 1:
                    return

    try:
        while True:
            show_status("\nPress Enter to START recording (or 'q' to quit)...", style="bold white")
            cmd = input().strip().lower()
            if cmd == 'q':
                break
            
            # 1. Start Recording
            play_start_listening_sound()
            recorder.start_recording()
            show_status("🎙️  Recording... Press Enter to STOP.", style="bold yellow")
            input()
            audio_path = recorder.stop_recording()
            play_stop_listening_sound()
            
            if not audio_path:
                show_error("No audio captured.")
                continue

            console.print(f"[dim]Saved audio: {audio_path}[/dim]")
            
            # 2. Transcribe
            with spinner("Transcribing audio..."):
                stt_result = await transcriber.transcribe(audio_path)
            
            if not stt_result.text:
                show_error("Could not understand anything, please try again.")
                continue
                
            console.print(f"[bold cyan]Heard:[/bold cyan] \"{stt_result.text}\"")
            
            # 3. Brain
            with spinner("Thinking..."):
                tool_call = await brain.process(stt_result.text)
            
            console.print(f"[dim]→ Planned action:[/dim] [bold]{tool_call.tool}[/bold] {tool_call.params}")
            
            if tool_call.tool == "help": # Check string literal
                console.print(f"[yellow]{tool_call.explanation}[/yellow]")
                continue
            
            # 4. Execute with Policy
            # Inject confirmation callback for smart commit (safe since in-process)
            if tool_call.tool == "git.smart_commit_push":
                tool_call.params["confirm_callback"] = lambda msg: Confirm.ask(f"[bold yellow]{msg}[/bold yellow]")
                
            await run_tool_with_policy(tool_call, stt_result.text)
                    
    except KeyboardInterrupt:
        console.print("\n[bold blue]GitVoice stopping...[/bold blue]")
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in main loop")

if __name__ == "__main__":
    asyncio.run(main())
