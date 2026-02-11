from llms.base import LLM

from google import genai
import time

class Gemini(LLM):

    def __init__(self, gemini_model_name: str, temp: float, max_length: int, gemini_token: str):

        self.temp = temp
        self.gemini_model_name = gemini_model_name
        self.max_length = max_length
        self.client = genai.Client(api_key=gemini_token)

    def generate_text_helper(self, prompt: str, num_sec=0, max_retries=5) -> str | None:

        if num_sec == max_retries:
            print("MAX RETRIES EXCEDED")
            return None
        time.sleep(2**(num_sec - 1))

        try:
            response = self.client.models.generate_content(
                model=self.gemini_model_name,
                contents=prompt,
            )
            if response.text == None:
                print("NONE RESPONSE:", response)
                return self.generate_text_helper(prompt, num_sec=num_sec+1, max_retries=max_retries)
            return response.text
        except Exception as e:
            print(f"Failed to parse response on attempt {num_sec+1}/{5}:", e)
            return self.generate_text_helper(prompt, num_sec=num_sec+1, max_retries=max_retries)

    def generate_text(self, prompt) -> str | None:
        return self.generate_text_helper(prompt, num_sec=0, max_retries=3)