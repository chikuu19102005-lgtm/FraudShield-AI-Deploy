from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "FraudShield-AI"
    }
)

response = client.chat.completions.create(
    model="arcee-ai/trinity-large-preview:free",
    messages=[
        {"role": "user", "content": "Say hello"}
    ]
)

print(response.choices[0].message.content)
