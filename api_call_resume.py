### DEEPSEEK ###
from openai import OpenAI
import os
from dotenv import load_dotenv

# Loads the environment file
load_dotenv()

# Deepseek R1 Free API
DEEPSEEK_R1_API_FREE = os.getenv("DEEPSEEK_R1_API_FREE")

# Clientside
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=DEEPSEEK_R1_API_FREE,
)

# Response generator
response = client.chat.completions.create(
    model="deepseek/deepseek-r1-0528:free",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Can you generate latex code for a sample resume?"},
    ],
    stream=False,
)

print(response.choices[0].message.content)
