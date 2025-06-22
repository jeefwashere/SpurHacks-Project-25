from flask import Flask, request, jsonify, send_file
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
        print(ai_response)
        return jsonify({
            'status': 'success',
            'analysis': ai_response
        })
    #this is jeff code 
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500
#this is jeff code 
OUTPUT_FILE_NAME = "output.tex"

def latex_escape(text):
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    for char, escape in replacements.items():
        text = text.replace(char, escape)
    return text


#############################################
# NAME: generate_latex
#
#
#
#############################################
def generate_latex(userSkills, jobSkills):
    # Deepseek R1 Free API
    DEEPSEEK_R1_API_FREE = os.getenv("DEEPSEEK_R1_API_FREE")

    if not DEEPSEEK_R1_API_FREE:
        raise ValueError("DeepSeek API key not found. Check .env file.")

    # Clientside
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=DEEPSEEK_R1_API_FREE,
    )

    user_skills_str = "\n".join(
        f"{latex_escape(k)}: {', '.join(map(latex_escape, v))}"
        for k, v in userSkills.items()
    )
    job_skills_str = "\n".join(
        f"{latex_escape(k)}: {', '.join(map(latex_escape, v))}"
        for k, v in jobSkills.items()
    )

    # Response generator
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {
                "role": "user",
                "content": f"""Given the user's skills and the job requirements, output a LaTeX-formatted skills section that highlights:
- Matching skills
- Transferable skills
- Any unique value the user brings

Use this format strictly:
\\section{{Skills}}
\\begin{{onecolentry}}
\\begin{{highlights}}
\\item ...
\\end{{highlights}}
\\end{{onecolentry}}

User Skills:
{user_skills_str}

Job Requirements:
{job_skills_str}

Only give the latex code, do not return ``` or ```latex
""",
            },
        ],
        stream=False,
    )

    latex_code = response.choices[0].message.content

    print("Finished")

    with open(OUTPUT_FILE_NAME, "w", encoding="UTF-8") as f:
        f.write(latex_code)

    return OUTPUT_FILE_NAME


def latexToPdf(fileName):

    if not os.path.exists(fileName):
        raise FileNotFoundError(f"{fileName} does not exist.")

    subprocess.run(["pdflatex", fileName], check=True)

    pdfFile = fileName.replace(".tex", ".pdf")

    if platform.system() == "Windows":
        os.startfile(pdfFile)
    else:
        print("OS incompatible. Windows only.")

@app.route("/process_data", methods=["POST"])
def process_data():
    data = request.get_json()
    userSkills = data.get("userSkills")
    jobSkills = data.get("jobSkills")

    if not userSkills or not jobSkills:
        return jsonify({"error": "Missing userSkills or jobSkills"}), 400

    try:
        tex_file = generate_latex(userSkills, jobSkills)
        latexToPdf(tex_file)
        return send_file(tex_file.replace(".tex", ".pdf"), as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
