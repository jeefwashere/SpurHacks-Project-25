from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Enable CORS to allow requests from the Chrome extension
CORS(app) 

# Initialize the OpenAI client for DeepSeek via OpenRouter
try:
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("DEEPSEEK_R1_API_FREE"),
    )
except Exception as e:
    client = None
    print(f"Error initializing OpenAI client: {e}")

@app.route('/')
def hello_world():
    return 'Hello, World! This is your Flask server.'

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    if not client:
        return jsonify({'error': 'AI client not initialized. Check your API key.'}), 500

    data = request.get_json()
    if not data or 'jobDescription' not in data:
        return jsonify({'error': 'Missing jobDescription'}), 400

    job_description = data['jobDescription']
    try:
        # Use the AI to analyze the job description
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {"role": "system", "content": "You are an expert resume assistant. Analyze the provided job description. and give me the answer at 30 seconds,Identify and list the key skills and qualifications required for this role. Categorize them under the only headings: 'Core Skills'. For each category, list only the skill or qualification name as a bullet point, without any additional explanations or descriptions. I don't want any special symbols, just plain text. "
},
                {"role": "user", "content": job_description},
            ],
            stream=False,
        )
        
        ai_response = response.choices[0].message.content

        return jsonify({
            'status': 'success',
            'analysis': ai_response
        })

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 