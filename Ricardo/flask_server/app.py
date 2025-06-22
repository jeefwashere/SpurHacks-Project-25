from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import subprocess
import platform
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
    print("✅ OpenAI client initialized successfully.")
except Exception as e:
    client = None
    print(f"❌ Error initializing OpenAI client: {e}")


@app.route("/")
def hello_world():
    return "Hello, World! This is your Flask server."


@app.route("/analyze", methods=["POST"])
def analyze_resume():
    print("\n--- Endpoint Hit: /analyze ---")
    if not client:
        print("❌ /analyze: AI client not initialized.")
        return jsonify({"error": "AI client not initialized. Check your API key."}), 500

    print("➡️  /analyze: Receiving request...")
    data = request.get_json()
    if not data or "jobDescription" not in data:
        print("❌ /analyze: Missing jobDescription in request.")
        return jsonify({"error": "Missing jobDescription"}), 400

    job_description = data["jobDescription"]
    print(
        f"📄 /analyze: Job Description received (first 80 chars): {job_description[:80]}..."
    )

    try:
        print("🤖 /analyze: Calling AI for analysis...")
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume assistant. Analyze the provided job description. and give me the answer at 30 seconds,Identify and list the key skills and qualifications required for this role. Categorize them under the only headings: 'Core Skills'. For each category, list only the skill or qualification name as a bullet point, without any additional explanations or descriptions. I don't want any special symbols, just plain text. ",
                },
                {"role": "user", "content": job_description},
            ],
            stream=False,
        )

        ai_response = response.choices[0].message.content
        print("✅ /analyze: Successfully received AI response.")
        print(f"📝 /analyze: Full AI Response: {ai_response}")
        print("⬅️  /analyze: Sending response back to client.")
        return jsonify({"jobDescription": job_description, "analysis": ai_response})
    except Exception as e:
        print(f"❌ /analyze: An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


def latex_escape(text):
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",  # Corrected curly brace escape
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    for char, escape in replacements.items():
        text = text.replace(char, escape)
    return text


def parse_job_skills(ai_response_text):
    """
    Parses the AI-generated text for job skills into a dictionary.
    """
    skills = {}
    lines = ai_response_text.strip().split("\n")
    current_category = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if the line is a header (e.g., "Core Skills")
        if not line.startswith(("-", "*")):
            current_category = line.replace(":", "").strip()
            if current_category not in skills:
                skills[current_category] = []
        # Check if the line is a skill under the current category
        elif current_category and line.startswith(("-", "*")):
            skill = line[1:].strip()
            if skill:
                skills[current_category].append(skill)

    return skills


#############################################
# NAME: generate_latex
#
# This function now generates ONLY the skills section snippet.
# It does NOT generate the full document preamble.
#############################################
def generate_latex(jobSkills, userSkills):
    print("\n--- Function Called: generate_latex ---")
    print(f"📄 generate_latex: Received userSkills: {userSkills}")
    print(f"📄 generate_latex: Received jobSkills: {jobSkills}")

    DEEPSEEK_R1_API_FREE = os.getenv("DEEPSEEK_R1_API_FREE")
    if not DEEPSEEK_R1_API_FREE:
        raise ValueError("DeepSeek API key not found. Check .env file.")

    # Use the globally initialized client
    # client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=DEEPSEEK_R1_API_FREE) # Removed redundancy

    user_skills_str = "\n".join(
        f"{latex_escape(k)}: {', '.join(map(latex_escape, v))}"
        for k, v in userSkills.items()
    )
    job_skills_str = "\n".join(
        f"{latex_escape(k)}: {', '.join(map(latex_escape, v))}"
        for k, v in jobSkills.items()
    )
    print("🤖 generate_latex: Calling AI for LaTeX generation (skills snippet only)...")

    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[
            {
                "role": "system",
                "content": """You are an expert LaTeX resume writer. Generate a FULL LaTeX resume document (including \\documentclass, \\begin{document}, etc.). Structure it like this:
**Rules:**
1. Return strictly ONLY LaTeX code (Strictly no ``` and ```latex or explanations).
2. Ensure the document compiles without errors.
3. Strictly tailor the generated resume's skills to the skills required by the job description.
4. Keep formatting clean and professional.
5. FULL DOCUMENT STRUCTURE (\\documentclass, \\begin{document}, etc.)
6. ESCAPED SPECIAL CHARACTERS (use \\& instead of &)
7. VALID ITEMIZE ENVIRONMENTS

\\documentclass[11pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[margin=0.75in]{geometry}
\\usepackage{enumitem}
\\setlist[itemize]{leftmargin=*}

\\title{Ricardo's Tailored Resume}
\\author{Ricardo Tieng}
\\date{\\today}

\\begin{document}
\\maketitle

\\section*{Skills}
\\begin{itemize}
    \\item **Matching Skills:** [List skills matching the job]
    \\item **Transferable Skills:** [List adaptable skills]
    \\item **Unique Value:** [Highlight unique strengths]
\\end{itemize}

[Rest of resume sections...]
\\end{document}""",
            },
            {
                "role": "user",
                "content": f"""
**Job Requirements:**
{job_skills_str}

**User Skills:**
{user_skills_str}

Generate a full LaTeX resume with a skills section optimized for this job. Only give pure latex code and nothing else.""",
            },
        ],
        stream=False,
    )

    latex_code = response.choices[0].message.content
    print("✅ generate_latex: Successfully received AI response (skills snippet).")

    print(f"✍️  generate_latex: Writing LaTeX code to {SKILLS_SNIPPET_FILE}...")
    with open(SKILLS_SNIPPET_FILE, "w", encoding="UTF-8") as f:
        f.write(latex_code)
    print(f"✅ generate_latex: Successfully wrote to {SKILLS_SNIPPET_FILE}.")
    return SKILLS_SNIPPET_FILE


def latexToPdf(fileName):
    print("\n--- Function Called: latexToPdf ---")
    print(f"📄 latexToPdf: Received fileName: {fileName}")
    if not os.path.exists(fileName):
        print(f"❌ latexToPdf: File not found: {fileName}")
        raise FileNotFoundError(f"{fileName} does not exist.")

    print(f"⚙️  latexToPdf: Running pdflatex command for {fileName}...")
    try:
        # Run pdflatex multiple times to ensure all cross-references/indexes are resolved
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", fileName],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", fileName],
            check=True,
            capture_output=True,
            text=True,
        )  # Run twice for safety
        print("✅ latexToPdf: pdflatex command completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ latexToPdf: pdflatex command failed.")
        print(f"   STDOUT: {e.stdout}")
        print(f"   STDERR: {e.stderr}")
        raise e

    if platform.system() == "Windows":
        print("🚀 latexToPdf: Opening PDF file on Windows...")
        os.startfile(fileName.replace(".tex", ".pdf"))
    else:
        print("ℹ️  latexToPdf: OS is not Windows, skipping auto-open.")


@app.route("/process_data", methods=["POST"])
def process_data():
    print("\n--- Endpoint Hit: /process_data ---")
    print("➡️  /process_data: Receiving request...")
    data = request.get_json()

    job_description_raw = data.get("jobDescription")

    if not job_description_raw:
        print("❌ /process_data: Missing jobDescription.")
        return jsonify({"error": "Missing jobDescription"}), 400

    # Hardcoded user skills for testing
    userSkills = {
        "Technical Skills": [
            "Python",
            "JavaScript",
            "SQL",
            "Git",
            "React",
            "C#",
            "HTML",
            "CSS",
            "C",
            "Microsoft Office",
            "SharePoint",
            "Power BI",
        ],
        "Soft Skills": [
            "Communication",
            "Teamwork",
            "Problem-solving",
            "Leadership",
            "Stakeholder Engagement",
            "Peer Mentoring",
            "Planning",
            "Time Management",
            "Research and Analysis",
            "Performance Tracking",
            "Internal Communication",
            "Interpersonal Communication",
            "Customer Service",
        ],
    }
    print(f"📄 /process_data: Using hardcoded userSkills: {userSkills}")

    try:
        # 1. Analyze the job description to get jobSkills
        print("▶️  /process_data: Calling AI to analyze job description...")
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume assistant. Analyze the provided job description. Identify and list the key skills and qualifications required for this role. Categorize them under the only headings: 'Core Skills'. For each category, list only the skill or qualification name as a bullet point, without any additional explanations or descriptions. I don't want any special symbols, just plain text.",
                },
                {"role": "user", "content": job_description_raw},
            ],
            stream=False,
        )
        ai_analysis_text = response.choices[0].message.content
        print("✅ /process_data: Successfully analyzed job description.")

        # Parse the AI response into the desired dictionary format
        jobSkills = parse_job_skills(ai_analysis_text)
        print(f"📄 /process_data: Parsed jobSkills: {jobSkills}")

        # 2. Generate the AI-based skills section snippet
        print("▶️  /process_data: Calling generate_latex for skills snippet...")
        latex_file = generate_latex(jobSkills, userSkills)
        print(f"✅ /process_data: generate_latex returned file: {latex_file}")

        # 6. Compile the full LaTeX document
        print("▶️  /process_data: Calling latexToPdf for final resume...")
        latexToPdf(latex_file)
        print("✅ /process_data: latexToPdf completed for final resume.")

        # 7. Send the final PDF
        print("⬅️  /process_data: Sending PDF file as attachment.")
        return send_file(latex_file.replace(".tex", ".pdf"), as_attachment=True)

    except Exception as e:
        print(f"❌ /process_data: An error occurred: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
