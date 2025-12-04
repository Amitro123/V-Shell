import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

class MetricsLogger:
    """Logs usage metrics to a JSONL file."""
    
    def __init__(self, log_file: str = "metrics.jsonl"):
        self.log_file = Path(log_file)
        
    def log(self, 
            text: str, 
            tool: str, 
            success: bool, 
            error: Optional[str] = None, 
            duration_ms: Optional[float] = None):
        """Log a single interaction event."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "tool": tool,
            "success": success,
            "error": error,
            "duration_ms": duration_ms
        }
        
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write metrics: {e}")
