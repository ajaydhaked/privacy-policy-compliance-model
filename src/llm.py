
import os
import time
from dotenv import load_dotenv
load_dotenv()


from openai import OpenAI
class llm:
    def __init__(self, model="gpt-5.4-mini"):
        self.model = model
        self.last_used_tokens = {}
        self.client = OpenAI(api_key=self.get_api_key())

    def get_api_key(self):
        return os.environ.get("OPENAI_API_KEY")

    def process_prompt(self, prompt_text):
        for attempt in range(5):
            try:
                print(f"llm call (attempt {attempt + 1}): {prompt_text[:20]}...")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt_text}
                    ]
                )

                usage = response.usage
                self.last_used_tokens = {
                    "input_tokens": usage.prompt_tokens if usage else 0,
                    "output_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0
                }

                output_text = response.choices[0].message.content
                print(f"llm response: {output_text[:20]}...")
                return output_text

            except Exception as e:
                print(f"An error occurred (attempt {attempt + 1}): {e}")
                time.sleep(2)

        return None
    


# from google import genai
# from random import randint
# class llm:
#     def __init__(self, model="gemini-3-flash-preview"):
#         self.model = model
#         self.idx = randint(0, 18)
#         self.last_used_tokens = {}

#     def get_api_key(self):
#         self.idx = (self.idx + 1) % 19
#         return os.environ.get(f"GEMINI_API_KEY_{self.idx}")

#     def process_prompt(self, prompt_text):

#         for attempt in range(5):
#             try:
#                 self.client = genai.Client(api_key=self.get_api_key())
#                 print(f"llm call (attempt {attempt + 1}): {prompt_text[:20]}...")
#                 response = self.client.models.generate_content(
#                     model=self.model,
#                     contents=prompt_text
#                 )
#                 self.last_used_tokens = {
#                     "input_tokens": response.usage_metadata.prompt_token_count,
#                     "output_tokens": response.usage_metadata.candidates_token_count,
#                     "total_tokens": response.usage_metadata.total_token_count
#                 }

#                 print(f"llm response: {response.text[:20]}...")
#                 return response.text
#             except Exception as e:
#                 print(f"An error occurred (attempt {attempt + 1}): {e}")
#                 time.sleep(2)
#         return None
