from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def chat_completion(messages):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.7,
    )
    return completion.choices[0].message.content