import logging
import json
from typing import Optional
from app.core.models import AppConfig, ToolCall, GitTool
from app.core.retry import with_retries

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
- git_pull: Pull from remote (params: remote [default origin], branch [optional])
- git_reset: Reset changes (params: mode [soft, mixed, hard], commits [default 1])
- git_checkout_branch: Switch branch (params: branch [required])
- git_create_branch: Create and switch to branch (params: branch [required])
- run_tests: Run the project's test suite
- smart_commit_push: Automatically stage, commit (with generated message), and push
- help: If the intent is unclear or not git related

Rules:
- For "commit", if no message is provided, generate a concise one based on context or use "Update".
- For "undo", usually means git_reset (soft by default).
- For "show me changes", use git_diff.
- For "what did I do", use git_status or git_log.
- For "run tests" or "test my code", use run_tests.
- For "smart commit" or "commit and push", use smart_commit_push.
- For "pull" or "update code", use git_pull.
- If the user asks to "fix conflicts", use 'help' for now as it's not fully implemented.

Output JSON format:
{
    "tool": "tool_name",
    "params": { ... },
    "confirmation_required": boolean,
    "explanation": "brief explanation"
}
Set confirmation_required = true for: commit, push, pull, reset, checkout (if switching branches might lose work), smart_commit_push.
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

    async def process(self, text: str) -> ToolCall:
        """Process natural language text into a structured ToolCall."""
        if not text:
            return ToolCall(tool=GitTool.HELP, explanation="I didn't hear anything.")
            
        logger.info(f"Processing intent for: {text}")
        
        async def _call_llm() -> ToolCall:
            if self.provider == "groq" and self.groq_client:
                # Wrap sync call in async for retry logic compatibility if needed, 
                # but with_retries handles sync functions if they return the value directly? 
                # No, with_retries expects an Awaitable. We need to wrap sync calls.
                # Actually, let's just make the inner function async and do the sync call inside.
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
            
            elif self.provider == "gemini" and self.gemini_model:
                # Gemini generate_content is sync by default in this SDK version usually
                response = self.gemini_model.generate_content(
                    f"{SYSTEM_PROMPT}\n\nUser: {text}",
                    generation_config={"response_mime_type": "application/json"}
                )
                data = json.loads(response.text)
                return ToolCall(**data)
            
            else:
                raise ValueError("No valid LLM provider configured.")

        try:
            # Use retry logic
            tool_call = await with_retries(lambda: _call_llm(), retries=2)
            
            # Heuristic Safety Override
            # Ensure dangerous commands always require confirmation, even if LLM forgot
            dangerous_keywords = ["commit", "push", "pull", "reset", "discard"]
            if any(k in text.lower() for k in dangerous_keywords) or \
               tool_call.tool in [GitTool.SMART_COMMIT_PUSH, GitTool.PUSH, GitTool.PULL, GitTool.RESET, GitTool.COMMIT]:
                tool_call.confirmation_required = True
                
            return tool_call
            
        except Exception as e:
            logger.error(f"Intent parsing failed after retries: {e}")
            return ToolCall(tool=GitTool.HELP, explanation=f"I couldn't understand that. Error: {e}")

    def generate_commit_message(self, diff: str) -> str:
        """Generate a concise commit message based on the diff."""
        if not diff:
            return "Update"
            
        prompt = f"""
        Generate a concise, conventional commit message (e.g., 'feat: add login', 'fix: resolve crash') 
        for the following git diff. Output ONLY the message, no quotes or explanation.
        
        Diff:
        {diff[:2000]}
        """
        
        try:
            if self.provider == "groq" and self.groq_client:
                completion = self.groq_client.chat.completions.create(
                    model=self.config.groq_model,
                    messages=[{"role": "user", "content": prompt}]
                )
                return completion.choices[0].message.content.strip()
                
            elif self.provider == "gemini" and self.gemini_model:
                response = self.gemini_model.generate_content(prompt)
                return response.text.strip()
                
        except Exception as e:
            logger.error(f"Failed to generate commit message: {e}")
            
        return "Update"
