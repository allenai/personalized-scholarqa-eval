from llms.base import LLM
import litellm

class LiteLLM(LLM):


    def __init__(self, model_name: str, temp: float, max_length: int, min_length: int = 64):

        self.temp = temp
        self.model_name = model_name
        self.max_length = max_length
        self.min_length = min_length
        self.cost = 0.0

    def generate_text_helper(self, prompt: str, num_sec=0, max_retries=5) -> str | None:

        if num_sec == max_retries:
            print("MAX RETRIES EXCEDED")
            return None

        try:
            
            response = litellm.completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_length,
                temperature=self.temp,
            )

            if self.cost == None:
                self.cost = 0.0

            curr_cost = response._hidden_params.get('response_cost', 0.0)
            self.cost += (curr_cost if curr_cost else 0.0)
            
            text = response.choices[0].message.content
            if text == None:
                return self.generate_text_helper(prompt, num_sec=num_sec+1, max_retries=max_retries)
            return text
        except Exception as e:
            print(f"Failed to parse response on attempt {num_sec+1}/{5}:", e)
            return self.generate_text_helper(prompt, num_sec=num_sec+1, max_retries=max_retries)

    def generate_text(self, prompt) -> str | None:
        return self.generate_text_helper(prompt, num_sec=0, max_retries=3)

    def generate_with_schema(self, prompt: str, schema) -> str | None:
        response = litellm.completion(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format=schema,
        )
        curr_cost = response._hidden_params.get('response_cost', 0.0)
        self.cost += (curr_cost if curr_cost else 0.0)
        return response.choices[0].message.content