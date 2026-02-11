from llms.base import LLM

import time
import anthropic

class Anthropic(LLM):

    def __init__(self, model_name: str, temp: float, max_length: int, anthropic_token: str):

        self.temp = temp
        self.model_name = model_name
        self.max_length = max_length
        self.client = anthropic.Anthropic(api_key=anthropic_token)

    def generate_text_helper(self, prompt, num_sec=0, max_retries=5):

        if num_sec == max_retries:
            print("MAX RETRIES EXCEDED")
            return None

        time.sleep(2**(num_sec))

        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=8192,
                temperature=1.0, # we set this just to enable thinking for profile generation
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                thinking={
                    "type": "enabled",
                    "budget_tokens": 4096
                },
            )
            return message.content[0].text

        except Exception as e:
            print('error:', e)
            return self.generate_text_helper(prompt, num_sec=num_sec+1, max_retries=max_retries)

    def generate_text(self, prompt):
        return self.generate_text_helper(prompt, num_sec=0, max_retries=3)