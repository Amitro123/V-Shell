import logging
import json
from typing import Optional
from app.core.models import AppConfig, ToolCall, GitTool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You are a Git assistant. Your job is to map natural language commands to specific Git tools.
You must return a JSON object matching the ToolCall schema.

Available tools:
- git_status: Check status
- git_log: Show commit history (params: n [default 5])
- git_diff: Show changes (params: file [optional])
- git_add_all: Stage all changes
- git_commit: Commit changes (params: message [required])
- git_push: Push to remote (params: remote [default origin], branch [optional])
- git_reset: Reset changes (params: mode [soft, mixed, hard], commits [default 1])
- git_checkout_branch: Switch branch (params: branch [required])
- git_create_branch: Create and switch to branch (params: branch [required])
- help: If the intent is unclear or not git related

Rules:
- For "commit", if no message is provided, generate a concise one based on context or use "Update".
- For "undo", usually means git_reset (soft by default).
- For "show me changes", use git_diff.
- For "what did I do", use git_status or git_log.
- If the user asks to "fix conflicts", use 'help' for now as it's not fully implemented.

Output JSON format:
{
    "tool": "tool_name",
    "params": { ... },
    "confirmation_required": boolean,
    "explanation": "brief explanation"
}
Set confirmation_required = true for: commit, push, reset, checkout (if switching branches might lose work).
"""

class Brain:
    """Interprets user intent using LLMs."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.provider = config.llm_provider
        self.groq_client = None
        self.gemini_model = None
        
        logger.info(f"Initializing Brain with provider: {self.provider}")
        
        if self.provider == "groq":
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=config.groq_api_key)
            except ImportError:
                logger.error("Groq library not installed.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=config.gemini_api_key)
                self.gemini_model = genai.GenerativeModel(config.gemini_model)
            except ImportError:
                logger.error("Google Generative AI library not installed.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

    def process(self, text: str) -> ToolCall:
        """Process natural language text into a structured ToolCall."""
        if not text:
            return ToolCall(tool=GitTool.HELP, explanation="I didn't hear anything.")
            
        logger.info(f"Processing intent for: {text}")
        
        if self.provider == "groq" and self.groq_client:
            try:
                completion = self.groq_client.chat.completions.create(
                    model=self.config.groq_model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": text}
                    ],
                    response_format={"type": "json_object"}
                )
                content = completion.choices[0].message.content
                data = json.loads(content)
                return ToolCall(**data)
            except Exception as e:
                logger.error(f"Groq intent parsing failed: {e}")
                return ToolCall(tool=GitTool.HELP, explanation=f"Failed to understand intent: {e}")
        
        elif self.provider == "gemini" and self.gemini_model:
            try:
                # Gemini structured output handling
                response = self.gemini_model.generate_content(
                    f"{SYSTEM_PROMPT}\n\nUser: {text}",
                    generation_config={"response_mime_type": "application/json"}
                )
                data = json.loads(response.text)
                return ToolCall(**data)
            except Exception as e:
                logger.error(f"Gemini intent parsing failed: {e}")
                return ToolCall(tool=GitTool.HELP, explanation=f"Failed to understand intent: {e}")
        
        else:
            logger.error("No valid LLM provider configured.")
            return ToolCall(tool=GitTool.HELP, explanation="Configuration error: No LLM provider available.")
