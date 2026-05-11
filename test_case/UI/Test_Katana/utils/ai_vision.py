import os
import json
import itertools
from time import sleep
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv
from loguru import logger

try:
    from .rag_knowledge import rag_kb
except ImportError:
    rag_kb = None

from pathlib import Path

# Load from possible .env locations: root or backend/
root_env = Path(__file__).parents[4] / ".env"
backend_env = Path(__file__).parents[4] / "backend" / ".env"

if root_env.exists():
    load_dotenv(root_env)
    logger.debug(f"Loaded configuration from root .env: {root_env}")
elif backend_env.exists():
    load_dotenv(backend_env)
    logger.debug(f"Loaded configuration from backend .env: {backend_env}")
else:
    # Default fallback to CWD-based load
    load_dotenv()

class AIVisionService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AIVisionService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'): return
        
        # 1. Parse Keys
        keys_str = os.getenv("GEMINI_API_KEYS")
        if not keys_str:
             # Fallback to single key
             keys_str = os.getenv("GEMINI_API_KEY")
        
        if not keys_str:
             logger.warning("GEMINI_API_KEY not configured. AI healing feature will be skipped.")
             self.api_keys = []
             self.model = None
             self.initialized = True
             return

        self.api_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        self.key_cycle = itertools.cycle(self.api_keys)
        self.current_key = next(self.key_cycle)
        self._configure_client(self.current_key)
        self.initialized = True

    def _configure_client(self, key):
        genai.configure(api_key=key)
        # Use Flash for basic background checks/logging
        self.model_flash = genai.GenerativeModel('gemini-2.0-flash')
        # Use Pro for specialized UI reasoning and pure vision navigation
        self.model_pro = genai.GenerativeModel('gemini-2.0-flash') # Fallback to Flash due to 404 on Pro Exp
        self.model = self.model_flash # default fallback

    def _rotate_key(self):
        if len(self.api_keys) <= 1: return False
        self.current_key = next(self.key_cycle)
        logger.warning(f"Rotate Key: Switching to next available key.")
        self._configure_client(self.current_key)
        return True

    def find_element(self, screenshot_path: str, instruction: str) -> dict:
        if not self.api_keys: return {"found": False, "error": "No API keys configured."}
        
        with open(screenshot_path, "rb") as image_file:
            image_data = image_file.read()
        
        prompt = f"""
        You are an Automation Testing Agent.
        Look at this screenshot of a web application.
        I need to interact with the element described as: "{instruction}".
        
        Please return a strictly valid JSON object with:
        "thought_process": analysis,
        "coordinates": {{ "x": <int>, "y": <int> }} (center of element).
        
        If not found, set "found": false.
        Return raw JSON only.
        """

        for attempt in range(len(self.api_keys) * 2):
            try:
                response = self.model.generate_content([
                    {'mime_type': 'image/png', 'data': image_data},
                    prompt
                ])
                res = self._parse_json(response.text)
                if res.get("thought_process"):
                    logger.info(f"🧠 AI Thoughts: {res['thought_process']}")
                return res
            except ResourceExhausted:
                if not self._rotate_key(): break
                sleep(1)
            except Exception as e:
                logger.error(f"AI Vision Error: {e}")
                break
        return {"found": False}

    def find_element_pure_vision(self, screenshot_path: str, instruction: str, history: list = None) -> dict:
        """
        Pure Vision-based identification with Introspection logic.
        Requires no DOM/SOM information.
        """
        if not self.api_keys: return {"found": False, "error": "No API keys."}
        
        with open(screenshot_path, "rb") as image_file:
            image_data = image_file.read()
            
        history_str = "None"
        if history:
            # format last 5 steps for context
            history_str = "\n".join([f"- {h}" for h in history[-5:]])
        
        prompt = f"""
        You are a Human-like QA Automation Agent testing a mobile-responsive web app.
        Current Step Objective: "{instruction}"
        
        Execution Context (Previous Steps):
        {history_str}
        
        Task:
        1. **Diagnose**: Look at the screenshot. Is the page in the correct state for the objective? 
           Check for: Blocking modals (Close/X buttons), Error messages, or if we are on the wrong tab.
        2. **Reason**: Identify the target element based *only* on visual cues (text, icons, buttons). 
           If the target is obscured by a modal, you MUST first identify the button to close/dismiss that modal.
        3. **Introspection**: Why is this the correct target? Double-check that it's not a background element.
        
        Return strictly valid JSON:
        {{
          "consciousness_diagnosis": "Explain the current page state and any obstacles found.",
          "thought_process": "Detailed reasoning for picking the coordinates.",
          "suggested_action": "GOAL_CLICK (standard), RECOVERY_CLICK (to close a modal), or ABORT (if a critical bug is found)",
          "coordinates": {{ "x": <int>, "y": <int> }},
          "suggested_locator": {{ "role": "button", "name": "Exact text", "description": "High-level goal description" }},
          "found": true
        }}
        
        Screen Resolution: 430 x 932
        Important: Return coordinates in the range of [0-430] for X and [0-932] for Y.
        Return raw JSON only.
        """

        for attempt in range(len(self.api_keys) * 3): # Increased to 3x the number of keys for retries
            try:
                logger.info(f"Connecting to Gemini (Self-Healing) - Attempt {attempt+1}...")
                response = self.model_pro.generate_content([
                    {'mime_type': 'image/png', 'data': image_data},
                    prompt
                ])
                res = self._parse_json(response.text)
                if res.get("consciousness_diagnosis"):
                    logger.info(f"🧠 AI Diagnosis: {res['consciousness_diagnosis']}")
                return res
            except Exception as e:
                logger.error(f"AI Pure Vision Error on Attempt {attempt+1}: {e}")
                # If rate-limited, increase the wait time slightly
                sleep_time = 3 if "429" in str(e) else 1
                if not self._rotate_key(): 
                     logger.warning("No more keys to rotate, sleep and retry same key.")
                     sleep(sleep_time)
                else:
                     sleep(sleep_time) # Brief pause to let the key rotation take effect
        return {"found": False}

    def _parse_json(self, text):
        try:
            raw = text.strip().replace("```json", "").replace("```", "")
            return json.loads(raw)
        except Exception as e:
            logger.error(f"JSON Parse Error: {e}. Raw response: {text[:200]}")
            return {"found": False, "error": "Invalid AI JSON"}

# Global instance
ai_vision = AIVisionService()
