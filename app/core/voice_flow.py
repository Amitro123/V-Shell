import logging
import asyncio
from rich.console import Console
from app.audio.recorder import AudioRecorder
from app.audio.stt import Transcriber

logger = logging.getLogger(__name__)

async def get_voice_confirmation(
    prompt: str,
    recorder: AudioRecorder,
    transcriber: Transcriber,
    console: Console,
    retries: int = 2
) -> bool:
    """
    Ask the user a yes/no question using text (and optional TTS),
    then listen to a short voice reply and interpret it as yes/no.

    Returns True for yes, False for no.
    """
    
    for attempt in range(retries + 1):
        # 1. Print prompt
        if attempt == 0:
            console.print(f"\n[bold yellow]Voice Confirmation Required:[/bold yellow] {prompt}")
            console.print("[dim](Say 'yes', 'sure', 'do it' OR 'no', 'stop', 'cancel')[/dim]")
        else:
            console.print(f"[yellow]I didn't catch that. {prompt} (Attempt {attempt}/{retries})[/yellow]")
        
        # 2. Record short audio (3 seconds)
        try:
            console.print("[red]Recording answer (3s)...[/red]")
            audio_path = recorder.record_once(duration=3)
        except Exception as e:
            logger.error(f"Recording failed: {e}")
            console.print(f"[bold red]Recording failed: {e}[/bold red]")
            return False

        # 3. Transcribe
        try:
            with console.status("[dim]Listening...[/dim]"):
                stt_result = await transcriber.transcribe(audio_path)
                text = stt_result.text.strip().lower()
                console.print(f"[dim]Heard: '{text}'[/dim]")
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            console.print(f"[bold red]Transcription failed: {e}[/bold red]")
            return False

        # 4. Interpret answer
        yes_keywords = ["yes", "yeah", "yep", "sure", "do it", "ok", "okay", "go ahead", "confirm"]
        no_keywords = ["no", "nope", "nah", "stop", "cancel", "abort", "don't", "wait"]

        if any(keyword in text for keyword in yes_keywords):
            return True
        elif any(keyword in text for keyword in no_keywords):
            return False
        
        # If unclear, loop again
        if attempt < retries:
            console.print("[yellow]Sorry, I didn't understand. Please say 'yes' or 'no'.[/yellow]")
    
    # Default to False if max retries reached
    console.print("[bold red]Voice confirmation failed. Defaulting to NO.[/bold red]")
    return False
