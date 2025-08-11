from __future__ import annotations

# Example provider using OpenAI; disabled for offline tests
# import os
# import openai
# from .provider import LLMProvider
#
# class OpenAIProvider(LLMProvider):
#     def __init__(self) -> None:
#         openai.api_key = os.getenv("OPENAI_API_KEY", "")
#
#     def generate(self, prompt: str, tone: str) -> str:
#         resp = openai.Completion.create(model="gpt-3.5-turbo", prompt=prompt)
#        return resp.choices[0].text
