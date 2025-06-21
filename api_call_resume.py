# from google import genai
# import os
# from dotenv import load_dotenv

# # Assigning api key env variable to a local variable
# GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# # The AI model used
# client = genai.Client(api_key=GEMINI_API_KEY)

# # Response mechanism for AI prompt
# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents=f"""Generate latex code for a resume based on these specifications:
#     %%%PLACEHOLDER%%%
#     """,
# )

# print(response.text)

### DEEPSEEK ###
from openai import OpenAI
import os

# Deepseek R1 Free API
DEEPSEEK_R1_API_FREE = os.environ.get("DEEPSEEK_R1_API_FREE")

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
