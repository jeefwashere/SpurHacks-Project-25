from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import subprocess
import platform
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OUTPUT_TEX = "output.tex"

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
    print("🤖 generate_latex: Calling AI for Latex generation...")

    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[
            {
                "role": "system",
                "content": r"""You are an expert LaTeX resume writer. Generate a FULL LaTeX resume document (including \\documentclass, \\begin{document}, etc.). Structure it like this:
**Rules:**
1. Return strictly ONLY LaTeX code (Strictly no ``` and ```latex or explanations).
2. Ensure the document compiles without errors.
3. Strictly tailor the generated resume's skills to the skills required by the job description.
4. Keep formatting clean and professional.
5. FULL DOCUMENT STRUCTURE (\\documentclass, \\begin{document}, etc.)
6. ESCAPED SPECIAL CHARACTERS (use \\& instead of &)
7. VALID ITEMIZE ENVIRONMENTS
8. STRICTLY DO NOT INCLUDE ``` and ```latex
9. ONLY PRODUCE LATEX CODE

---- STRICTLY FOLLOW THIS TEMPLATE ----
\\documentclass[11pt]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[margin=0.75in]{geometry}
\\usepackage{enumitem}
\\setlist[itemize]{leftmargin=*}

\documentclass[10pt, letterpaper]{article}
\usepackage[utf8]{inputenc}

% Packages:
\usepackage[
    ignoreheadfoot, % set margins without considering header and footer
    top=2 cm, % seperation between body and page edge from the top
    bottom=2 cm, % seperation between body and page edge from the bottom
    left=2 cm, % seperation between body and page edge from the left
    right=2 cm, % seperation between body and page edge from the right
    footskip=1.0 cm, % seperation between body and footer
    % showframe % for debugging 
]{geometry} % for adjusting page geometry
\usepackage{titlesec} % for customizing section titles
\usepackage{tabularx} % for making tables with fixed width columns
\usepackage{array} % tabularx requires this
\usepackage[dvipsnames]{xcolor} % for coloring text
\definecolor{primaryColor}{RGB}{0, 0, 0} % define primary color
\usepackage{enumitem} % for customizing lists
\usepackage{fontawesome5} % for using icons
\usepackage{amsmath} % for math
\usepackage[
    pdftitle={John Doe's CV},
    pdfauthor={John Doe},
    pdfcreator={LaTeX with RenderCV},
    colorlinks=true,
    urlcolor=primaryColor
]{hyperref} % for links, metadata and bookmarks
\usepackage[pscoord]{eso-pic} % for floating text on the page
\usepackage{calc} % for calculating lengths
\usepackage{bookmark} % for bookmarks
\usepackage{lastpage} % for getting the total number of pages
\usepackage{changepage} % for one column entries (adjustwidth environment)
\usepackage{paracol} % for two and three column entries
\usepackage{ifthen} % for conditional statements
\usepackage{needspace} % for avoiding page brake right after the section title
\usepackage{iftex} % check if engine is pdflatex, xetex or luatex

% Ensure that generate pdf is machine readable/ATS parsable:
\ifPDFTeX
    \input{glyphtounicode}
    \pdfgentounicode=1
    \usepackage[T1]{fontenc}
    \usepackage[utf8]{inputenc}
    \usepackage{lmodern}
\fi

\usepackage{times}

% Fix Unicode minus sign
\DeclareUnicodeCharacter{2212}{-}

% Some settings:
\raggedright
\AtBeginEnvironment{adjustwidth}{\partopsep0pt} % remove space before adjustwidth environment
\pagestyle{empty} % no header or footer
\setcounter{secnumdepth}{0} % no section numbering
\setlength{\parindent}{0pt} % no indentation
\setlength{\topskip}{0pt} % no top skip
\setlength{\columnsep}{0.15cm} % set column seperation
\pagenumbering{gobble} % no page numbering

%\titleformat{\section}{\needspace{4\baselineskip}\bfseries\large}{}{0pt}{}[\vspace{1pt}\titlerule]

\titlespacing{\section}{
    % left space:
    -1pt
}{
    % top space:
    0.3 cm
}{
    % bottom space:
    0.2 cm
} % section title spacing

\renewcommand\labelitemi{$\vcenter{\hbox{\small$\bullet$}}$} % custom bullet points
\newenvironment{highlights}{
    \begin{itemize}[
        topsep=0.10 cm,
        parsep=0.10 cm,
        partopsep=0pt,
        itemsep=0pt,
        leftmargin=0 cm + 10pt
    ]
}{
    \end{itemize}
} % new environment for highlights


\newenvironment{highlightsforbulletentries}{
    \begin{itemize}[
        topsep=0.10 cm,
        parsep=0.10 cm,
        partopsep=0pt,
        itemsep=0pt,
        leftmargin=10pt
    ]
}{
    \end{itemize}
} % new environment for highlights for bullet entries

\newenvironment{onecolentry}{
    \begin{adjustwidth}{
        0 cm + 0.00001 cm
    }{
        0 cm + 0.00001 cm
    }
}{
    \end{adjustwidth}
} % new environment for one column entries

\newenvironment{twocolentry}[2][]{
    \onecolentry
    \def\secondColumn{#2}
    \setcolumnwidth{\fill, 4.5 cm}
    \begin{paracol}{2}
}{
    \switchcolumn \raggedleft \secondColumn
    \end{paracol}
    \endonecolentry
} % new environment for two column entries

\newenvironment{threecolentry}[3][]{
    \onecolentry
    \def\thirdColumn{#3}
    \setcolumnwidth{, \fill, 4.5 cm}
    \begin{paracol}{3}
    {\raggedright #2} \switchcolumn
}{
    \switchcolumn \raggedleft \thirdColumn
    \end{paracol}
    \endonecolentry
} % new environment for three column entries

\newenvironment{header}{
    \setlength{\topsep}{0pt}\par\kern\topsep\centering\linespread{1.5}
}{
    \par\kern\topsep
} % new environment for the header

\newcommand{\placelastupdatedtext}{% \placetextbox{<horizontal pos>}{<vertical pos>}{<stuff>}
  \AddToShipoutPictureFG*{% Add <stuff> to current page foreground
    \put(
        \LenToUnit{\paperwidth-2 cm-0 cm+0.05cm},
        \LenToUnit{\paperheight-1.0 cm}
    ){\vtop{{\null}\makebox[0pt][c]{
        \small\color{gray}\textit{Last updated in July 2024}\hspace{\widthof{Last updated in July 2024}}
    }}}%
  }%
}%

\begin{document}
    \newcommand{\AND}{\unskip
        \cleaders\copy\ANDbox\hskip\wd\ANDbox
        \ignorespaces
    }
    \newsavebox\ANDbox
    \sbox\ANDbox{$|$}

    \begin{header}
        \fontsize{ 40 pt}{40 pt}\selectfont Ricardo Gao

        \vspace{7 pt}

        \normalsize
        \mbox{Waterloo,ON}%
        \kern 5.0 pt%
        \AND%
        \kern 5.0 pt%
        \mbox{\href{mailto:gaozhe0011@gmail.com}{gaozhe0011@gmail.com}}%
        \kern 5.0 pt%
        \AND%
        \mbox{\href{tel:+13828852156}{+1 382 885 2156}}%
        \kern 5.0 pt%
        \AND%
                \\
        \mbox{\href{https://www.ricardogao.me/}{Personal Website}}%
        \kern 5.0 pt%
        \AND%
        \mbox{\href{https://www.linkedin.com/in/ricardo-gao}{Linkedin}}%
        \kern 5.0 pt%
        \AND%
        \mbox{\href{https://github.com/RicadoGz}{Github}}%
        
    \end{header}
    \vspace{-12pt}
\vspace{-12pt}
 \section{Skills}
 \vspace{-13pt}
\hrulefill\\
\small
\begin{onecolentry}
\begin{highlights}
    \item Technical Skills: \textbf{HTML},\textbf{CSS},\textbf{JavaScript},\textbf{C\#},C,python,Microsoft Office (Word, Outlook, Teams, PowerPoint), SharePoint, Power BI
    \item Project \& Organizational Skills: Leadership, Stakeholder Engagement, Peer Mentoring, Planning, Time Management
    \item Analytical Skills: Research and Analysis, Problem Solving, Performance Tracking
    \item Communication Skills: Internal Communication, Interpersonal Communication, Customer Service
\end{highlights}

\end{onecolentry}


 \vspace{-8pt}
 \section{Education}
\vspace{-13pt}
\hrulefill
\vspace{+3pt}
\begin{onecolentry}
 {\normalsize \textbf{Conestoga College}} \hfill {2024 Sep - Dec 2028}\\
 \vspace{+3pt}
 {Software Engineering Technology} \hfill {3.93/4.0}\\
  \vspace{-8pt}
  
   
\end{onecolentry}
 
\section{Professornal Experience}
\vspace{-12pt}
\hrulefill
\begin{onecolentry
    {\normalsize \textbf{Peer-Assisted Learning Leader for C Programming}} \hfill {(Jan 2025 – Apr 2025)}\\
    {Conestoga College} \hfill {Waterloo, ON}\\
    \begin{highlights}
        \item Utilized \textbf{SharePoint} to manage and distribute course materials, consistently uploading \textbf{at least 4 resources weekly over 14 weeks}, ensuring structured and accessible content delivery for students.
        \item Created  \textbf{session plans using Microsoft Word}, preparing \textbf{two plans per week} to guide and optimize weekly peer learning sessions.
        \item Facilitated direct communication with students via \textbf{Microsoft Teams}, providing real-time support, feedback, and follow-up outside of scheduled sessions.
        \item Helped a student improve their quiz score from \textbf{20\% to 90\%} and assignment grade from \textbf{40\% to 99.5\%} within 6 weeks, demonstrating a \textbf{400\% performance increase} through personalized guidance and consistent support.

        \item Utilized \textbf{Power BI} to create data visualizations tracking student attendance and performance improvements over time, enabling data-driven reflection and continuous support adjustments.

    \end{highlights}
\end{onecolentry}
\begin{onecolentry}
    {\normalsize \textbf{Executive Leader}} \hfill {(Oct \textbf{2024} – Present)}\\
    {Google Developer Group} \hfill {Waterloo, ON}\\
    \begin{highlights}
        \item Organized and participated in over \textbf{5} events with \textbf{30+} attendees each, focusing on student success through applied tech learning.
        \item \textbf{Collaborated} with \textbf{internal college club}s and external partners including Wilfrid Laurier University to co-host workshops and community events.
        \item Utilized \textbf{SharePoint}, \textbf{Google Drive}, and \textbf{PowerPoint} for event planning, file sharing, and professional presentations.
        \item Maintained over \textbf{80\%} attendance in weekly team meetings, demonstrating strong time management and commitment.
        \item Fostered student engagement and peer support by building a \textbf{500+} member community—the largest student group at Conestoga College.
    \end{highlights}
\end{onecolentry}






\vspace{-12pt}
\section{Project Experience}
\vspace{-12pt}
\hrulefill\\
\begin{onecolentry}
    {\normalsize \textbf{Personal Web Developer}} \hfill {(May 2024 – Present)}\\
    {Self-Initiated Project} \hfill {Waterloo, ON}\\
    \begin{highlights}
        \item Designed, developed, and hosted a personal portfolio website using \textbf{HTML}, \textbf{CSS}, and \textbf{JavaScript}, showcasing projects and technical skills.
        \item Implemented responsive design for accessibility on desktop and mobile using CSS Grid and Flexbox.
        \item Deployed website using GitHub Pages and optimized performance through image compression and script minimization.
        \item Continuously maintained and updated content to reflect latest accomplishments and learning progress.
    \end{highlights}
\end{onecolentry}

\begin{onecolentry}
    {\normalsize \textbf{C\# Vehicle Management System Project}} \hfill {(Jan 2025 – Mar 2025)}\\
    {Academic Project} \hfill {Conestoga College}\\
    \begin{highlights}
        \item Developed a full-featured vehicle management system using \textbf{C\#} and \textbf{.NET}, incorporating course skills such as \textbf{inheritance}, \textbf{interfaces}, \textbf{delegates}, and \textbf{exception handling}.
        \item Designed a domain-driven structure and applied OOP principles for maintainability and scalability.
        \item Overrode the \texttt{IComparable} interface to enable customized vehicle sorting by mileage and model year.
        \item Integrated \textbf{interface-based architecture} to separate UI and logic, leveraging \texttt{IRepository} patterns and dependency injection.
        \item Applied \textbf{data visualization} with summary views for performance metrics, saving over \textbf{30\%} in manual processing time.
    \end{highlights}
\end{onecolentry}




\end{document}""",
            },
            {
                "role": "user",
                "content": f"""
**Job Requirements:**
{job_skills_str}

**User Skills:**
{user_skills_str}

Generate a full LaTeX resume with a skills section optimized for this job. Only give pure latex code and nothing else. STRICTLY NO ``` and ```latex.""",
            },
        ],
        stream=False,
    )

    latex_code = response.choices[0].message.content
    print("✅ generate_latex: Successfully received AI response (skills snippet).")

    print(f"✍️  generate_latex: Writing LaTeX code to {OUTPUT_TEX}...")
    with open(OUTPUT_TEX, "w", encoding="UTF-8") as f:
        f.write(latex_code)
    print(f"✅ generate_latex: Successfully wrote to {OUTPUT_TEX}.")
    return OUTPUT_TEX


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
