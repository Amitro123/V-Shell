import logging
import sys
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from app.config import load_config
from app.audio.recorder import AudioRecorder
from app.audio.stt import Transcriber
from app.llm.router import Brain
from app.core.executor import GitExecutor
from app.core.models import GitTool

# Configure logging
logging.basicConfig(
    level=logging.WARNING, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("gitvoice")

console = Console()

def main():
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
            executor = GitExecutor(config)
        except Exception as e:
            console.print(f"[bold red]Initialization failed:[/bold red] {e}")
            return

    console.print("[dim]Press Ctrl+C to exit[/dim]")
    
    try:
        while True:
            console.print("\n[bold blue]Press Enter to record a new voice command (or 'q' to quit)...[/bold blue]")
            cmd = input().strip().lower()
            if cmd == 'q':
                break
            
            # 1. Record
            audio_path = recorder.record_once()
            console.print(f"[dim]Recorded audio: {audio_path}[/dim]")
            
            # 2. Transcribe
            with console.status("[dim]Transcribing...[/dim]"):
                stt_result = transcriber.transcribe(audio_path)
            
            if not stt_result.text:
                console.print("[red]Could not understand anything, please try again.[/red]")
                continue
                
            console.print(f"[bold]Heard:[/bold] \"{stt_result.text}\"")
            
            # 3. Brain
            with console.status("[dim]Thinking...[/dim]"):
                tool_call = brain.process(stt_result.text)
            
            console.print(f"[dim]Planned action:[/dim] {tool_call.tool.value} ({tool_call.params})")
            
            if tool_call.tool == GitTool.HELP:
                console.print(f"[yellow]{tool_call.explanation}[/yellow]")
                continue
            
            # 4. Confirmation
            if tool_call.confirmation_required and config.require_confirmation_writes:
                explanation = tool_call.explanation or f"Execute {tool_call.tool.value}?"
                if not Confirm.ask(f"[bold red]{explanation}[/bold red]"):
                    console.print("[red]Cancelled.[/red]")
                    continue
            
            # 5. Execute
            with console.status("[dim]Executing...[/dim]"):
                result = executor.execute(tool_call)
            
            if result.success:
                console.print(Panel(result.stdout, title="[bold green]Success[/bold green]", border_style="green"))
            else:
                console.print(Panel(result.stderr, title="[bold red]Error[/bold red]", border_style="red"))
                    
    except KeyboardInterrupt:
        console.print("\n[bold blue]GitVoice stopping...[/bold blue]")
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {e}")
        logger.exception("Unexpected error in main loop")

if __name__ == "__main__":
    main()
