from llms.base import LLM

from openai import OpenAI
import time

class OpenAILLM(LLM):

    def __init__(self, openai_model_name: str, temp: float, max_length: int, openai_token: str):

        self.temp = temp
        self.openai_model_name = openai_model_name
        self.max_length = max_length
        self.openai_token = openai_token

    def generate_text_helper(self, prompt: str, num_sec=0, max_retries=5) -> str | None:

        if num_sec == max_retries:
            print("MAX RETRIES EXCEDED")
            return None

        try:
            client = OpenAI(api_key=self.openai_token)

            if 'o3' in self.openai_model_name or 'o4' in self.openai_model_name or 'gpt-5' in self.openai_model_name:
                response = client.responses.create(
                    model=self.openai_model_name,
                    input=[
                        {"role": "user", "content": [{"type": "input_text", "text": prompt }]},
                    ],
                    text={"format": {"type": "text"}},
                    reasoning={
                        "effort": "high"
                    },
                    tools=[],
                    store=True
                )
                return response.output[-1].content[0].text
            else:
                response = client.chat.completions.create(
                            model=self.openai_model_name,
                            messages=[
                                {"role": "user", "content": prompt}
                            ],
                            max_completion_tokens=self.max_length,
                            temperature=self.temp)
            return response.choices[0].message.content

        except Exception as e:
            time.sleep(2**(num_sec))
            print(f"Failed to parse response on attempt {num_sec+1}/{5}:", e)
            return self.generate_text_helper(prompt, num_sec=num_sec+1, max_retries=max_retries)

    def generate_text(self, prompt) -> str | None:
        return self.generate_text_helper(prompt, num_sec=0, max_retries=3)