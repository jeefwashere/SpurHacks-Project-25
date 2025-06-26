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

@app.route('/')
def hello_world():
    return 'Hello, World! This is your Flask server.'

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    print("\n--- Endpoint Hit: /analyze ---")
    if not client:
        print("❌ /analyze: AI client not initialized.")
        return jsonify({'error': 'AI client not initialized. Check your API key.'}), 500

    print("➡️  /analyze: Receiving request...")
    data = request.get_json()
    if not data or 'jobDescription' not in data:
        print("❌ /analyze: Missing jobDescription in request.")
        return jsonify({'error': 'Missing jobDescription'}), 400

    job_description = data['jobDescription']
    print(f"📄 /analyze: Job Description received (first 80 chars): {job_description[:80]}...")
    
    try:
        print("🤖 /analyze: Calling AI for analysis...")
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {"role": "system", "content": "You are an expert resume assistant. Analyze the provided job description. and give me the answer at 30 seconds,Identify and list the key skills and qualifications required for this role. Categorize them under the only headings: 'Core Skills'. For each category, list only the skill or qualification name as a bullet point, without any additional explanations or descriptions. I don't want any special symbols, just plain text. "},
                {"role": "user", "content": job_description},
            ],
            stream=False,
        )
        
        ai_response = response.choices[0].message.content
        print("✅ /analyze: Successfully received AI response.")
        print(f"📝 /analyze: Full AI Response: {ai_response}")
        print("⬅️  /analyze: Sending response back to client.")
        return jsonify({
            'jobDescription': job_description,
            'analysis': ai_response
        })
    except Exception as e:
        print(f"❌ /analyze: An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

# Define the name for the AI-generated skills snippet
SKILLS_SNIPPET_FILE = "ai_generated_skills.tex"
# Define the name for the full resume LaTeX file
FINAL_RESUME_FILE = "final_resume.tex" # This will be the combined template + AI content

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
    lines = ai_response_text.strip().split('\n')
    current_category = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if the line is a header (e.g., "Core Skills")
        if not line.startswith(('-', '*')):
            current_category = line.replace(":", "").strip()
            if current_category not in skills:
                skills[current_category] = []
        # Check if the line is a skill under the current category
        elif current_category and line.startswith(('-', '*')):
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

    user_skills_str = "\n".join(f"{latex_escape(k)}: {', '.join(map(latex_escape, v))}" for k, v in userSkills.items())
    job_skills_str = "\n".join(f"{latex_escape(k)}: {', '.join(map(latex_escape, v))}" for k, v in jobSkills.items())
    print("🤖 generate_latex: Calling AI for LaTeX generation (skills snippet only)...")
    
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[
            {"role": "system", "content": "You are a helpful assistant. Generate only the LaTeX code for the skills section, including \\section{Skills}, \\begin{onecolentry}, and \\begin{highlights}. Do NOT include \\documentclass, \\usepackage, \\begin{document}, or \\end{document}. Focus on providing matching, transferable, and unique value skills. Format as \\item \\textbf{Category: } Skill 1, Skill 2. Only give the latex code, do not return ``` or ```latex"},
            {"role": "user", "content": f"""Given the user's skills and the job requirements, output a LaTeX-formatted skills section that highlights:
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
"""},
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
        subprocess.run(["pdflatex", "-interaction=nonstopmode", fileName], check=True, capture_output=True, text=True)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", fileName], check=True, capture_output=True, text=True) # Run twice for safety
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
    
    job_description_raw = data.get('jobDescription')

    if not job_description_raw:
        print("❌ /process_data: Missing jobDescription.")
        return jsonify({"error": "Missing jobDescription"}), 400

    # Hardcoded user skills for testing
    userSkills = {
        "Technical Skills": ["Python", "JavaScript", "SQL", "Git", "React", "C#", "HTML", "CSS", "C", "Microsoft Office", "SharePoint", "Power BI"],
        "Soft Skills": ["Communication", "Teamwork", "Problem-solving", "Leadership", "Stakeholder Engagement", "Peer Mentoring", "Planning", "Time Management", "Research and Analysis", "Performance Tracking", "Internal Communication", "Interpersonal Communication", "Customer Service"]
    }
    print(f"📄 /process_data: Using hardcoded userSkills: {userSkills}")

    try:
        # 1. Analyze the job description to get jobSkills
        print("▶️  /process_data: Calling AI to analyze job description...")
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[
                {"role": "system", "content": "You are an expert resume assistant. Analyze the provided job description. Identify and list the key skills and qualifications required for this role. Categorize them under the only headings: 'Core Skills'. For each category, list only the skill or qualification name as a bullet point, without any additional explanations or descriptions. I don't want any special symbols, just plain text."},
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
        ai_skills_snippet_file = generate_latex(jobSkills, userSkills)
        print(f"✅ /process_data: generate_latex returned file: {ai_skills_snippet_file}")

        # 3. Read the full resume template
        full_template_path = os.path.join(os.getcwd(), 'full_resume_template.tex') # Ensure this path is correct
        if not os.path.exists(full_template_path):
             print(f"❌ /process_data: Full resume template not found at {full_template_path}")
             return jsonify({"error": f"Full resume template not found at {full_template_path}"}), 500

        with open(full_template_path, 'r', encoding='utf-8') as f:
            full_template_content = f.read()

        # 4. Read the AI-generated skills content
        with open(ai_skills_snippet_file, 'r', encoding='utf-8') as f:
            ai_skills_content = f.read()

        # 5. Integrate the AI-generated skills into the template
        # Find the line where the existing Skills section starts and replace it
        # This assumes your template has a clear marker for the skills section, e.g., "\section{Skills}"
        # A more robust way might be to identify a specific placeholder.
        # For simplicity, we'll replace the entire existing skills section.
        # Original:
        #  \section{Skills}
        #  \vspace{-13pt}
        # \hrulefill\\
        # \small
        # \begin{onecolentry}
        # \begin{highlights}
        #     \item Technical Skills: \textbf{HTML},\textbf{CSS},\textbf{JavaScript},\textbf{C\#},C,python,Microsoft Office (Word, Outlook, Teams, PowerPoint), SharePoint, Power BI
        #     \item Project \& Organizational Skills: Leadership, Stakeholder Engagement, Peer Mentoring, Planning, Time Management
        #     \item Analytical Skills: Research and Analysis, Problem Solving, Performance Tracking
        #     \item Communication Skills: Internal Communication, Interpersonal Communication, Customer Service
        # \end{highlights}
        # \end{onecolentry}
        
        # You need to find the exact start and end of the skills section to replace it.
        # A simple string replace might work if the template is static, but robust parsing is better.
        # For now, let's assume the AI-generated content WILL REPLACE the existing Skills section.
        
        # Define a placeholder in your full_resume_template.tex like:
        # % -- AI_GENERATED_SKILLS_SECTION --
        # And then replace it.
        
        # If you want to replace the whole existing skills section in your template:
        # Let's define the start and end markers for replacement based on your template content
        # Start marker: \section{Skills}
        # End marker: \section{Education} (or whatever follows it)
        
        # Simpler approach: Create a placeholder in your template and replace it.
        # In your 'full_resume_template.tex', add this exact line where you want the AI skills:
        # %%% AI_SKILLS_PLACEHOLDER %%%
        
        # Then, modify the AI prompt in generate_latex to NOT include \section{Skills} if you want the main template to control that.
        # Let's adjust generate_latex's prompt. It should generate ONLY the contents of onecolentry and highlights.
        
        # REVISITING generate_latex: It should output only the content *inside* the skill section, not the section itself.
        # This means the prompt needs to change in generate_latex (already adjusted above for system message).
        
        # Assuming AI generates content for `\begin{onecolentry} ... \end{onecolentry}`
        
        # Replace the entire existing Skills section in the template with the AI-generated content.
        # This requires careful string manipulation.
        
        # Find the existing skills section to replace it
        start_marker = r"\section{Skills}"
        end_marker = r"\section{Education}" # Assuming Education always follows Skills
        
        # Find the content between these markers
        start_index = full_template_content.find(start_marker)
        end_index = full_template_content.find(end_marker, start_index)
        
        if start_index == -1 or end_index == -1:
            print("❌ /process_data: Could not find markers for Skills section replacement.")
            # Fallback if markers aren't found or use a simpler insertion point
            # For now, let's assume the template is structured for direct replacement
            # or you'll manually edit it.
            # As a temporary workaround, if no placeholder, we can just insert it at the end
            # or at a fixed point after the header. This is less robust.
            # For now, let's just make sure the AI prompt generates the full section.
            
            # Since the AI generates `\section{Skills}...`, we'll replace the existing one entirely.
            # A more robust solution for templates would use `\input{ai_generated_skills.tex}`.
            # But since the user wants to *replace* the existing skills, we'll do string manipulation.
            
            # This is risky, but directly replacing the whole block is what's implied.
            # Better way: Modify the template to have a placeholder, e.g., `%%% AI_SKILLS_HERE %%%`
            # and replace that.
            
            # Let's define a placeholder for simplicity and robustness.
            # You *must* add `%%% AI_SKILLS_HERE %%%` in your `full_resume_template.tex`
            # exactly where you want the AI-generated skills section to appear.
            # Example:
            # ... header ...
            # %%% AI_SKILLS_HERE %%%
            # \section{Education}
            # ... rest of resume ...
            
            final_resume_content = full_template_content.replace('%%% AI_SKILLS_HERE %%%', ai_skills_content)
            print("✅ /process_data: Successfully integrated AI skills into template.")
        else:
             # This branch is for replacing existing content.
             # Slice the string to keep content before and after the skills section.
            prefix = full_template_content[:start_index]
            suffix = full_template_content[end_index:]
            
            # Combine
            final_resume_content = prefix + ai_skills_content + suffix
            print("✅ /process_data: Successfully replaced existing Skills section with AI content.")


        # Write the combined content to a new file that pdflatex will compile
        with open(FINAL_RESUME_FILE, 'w', encoding='utf-8') as f:
            f.write(final_resume_content)
        print(f"✍️  /process_data: Wrote final resume to {FINAL_RESUME_FILE}.")

        # 6. Compile the full LaTeX document
        print("▶️  /process_data: Calling latexToPdf for final resume...")
        latexToPdf(FINAL_RESUME_FILE)
        print("✅ /process_data: latexToPdf completed for final resume.")

        # 7. Send the final PDF
        print("⬅️  /process_data: Sending PDF file as attachment.")
        return send_file(FINAL_RESUME_FILE.replace(".tex", ".pdf"), as_attachment=True)

    except Exception as e:
        print(f"❌ /process_data: An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)