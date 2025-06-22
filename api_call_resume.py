### DEEPSEEK ###
import subprocess
import os
import platform
from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file

# Loads the environment file
load_dotenv()

app = Flask(__name__)
# Constant for output file name
OUTPUT_FILE_NAME = "output.tex"


@app.route("/process_data", methods=["POST"])
#############################################
# NAME:
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

    user_skills_str = "\n".join(f"{k}: {', '.join(v)}" for k, v in userSkills.items())
    job_skills_str = "\n".join(f"{k}: {', '.join(v)}" for k, v in jobSkills.items())

    # Response generator
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {
                "role": "user",
                "content": rf"""Given the user's skills and the job requirements, output a LaTeX-formatted skills section that highlights:
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

Job Skills:
{job_skills_str}

Do not include \\documentclass or any preamble.
Only return valid LaTeX code that fits into the given template section.
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

    subprocess.run(["pdflatex", fileName], check="True")

    pdfFile = fileName.replace(".tex", ".pdf")

    if platform.system() == "Windows":
        os.startfile(pdfFile)
    else:
        print("OS incompatible. Windows only.")


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
