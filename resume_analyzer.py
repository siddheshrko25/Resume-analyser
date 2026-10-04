import tkinter as tk
from tkinter import filedialog, messagebox
from pypdf import PdfReader


# ============================================================
# HIREDREADY - RESUME ANALYZER
# ============================================================

# ---------------- COLORS ----------------

BG = "#F5F1E8"
CARD = "#FFFFFF"
GREEN = "#176B5B"
GREEN_DARK = "#0F5145"
TEXT = "#29231D"
MUTED = "#71685E"
RED = "#B64A4A"
BORDER = "#DDD6CB"


# ============================================================
# GLOBAL VARIABLES
# ============================================================

selected_file_path = None

file_name = None
analyze_button = None

canvas = None
content_frame = None
canvas_window = None


# ============================================================
# MAIN WINDOW
# ============================================================

window = tk.Tk()

window.title("HireReady - Resume Analyzer")

window.geometry("1000x750")

window.minsize(800, 600)

window.configure(bg=BG)


# ============================================================
# MAIN FRAME
# ============================================================

main_frame = tk.Frame(
    window,
    bg=BG
)

main_frame.pack(
    fill="both",
    expand=True
)


# ============================================================
# CANVAS
# ============================================================

canvas = tk.Canvas(
    main_frame,
    bg=BG,
    highlightthickness=0,
    bd=0
)

canvas.pack(
    side="left",
    fill="both",
    expand=True
)


# ============================================================
# SCROLLBAR
# ============================================================

scrollbar = tk.Scrollbar(
    main_frame,
    orient="vertical",
    command=canvas.yview
)

scrollbar.pack(
    side="right",
    fill="y"
)

canvas.configure(
    yscrollcommand=scrollbar.set
)


# ============================================================
# CONTENT FRAME
# ============================================================

content_frame = tk.Frame(
    canvas,
    bg=BG
)

canvas_window = canvas.create_window(
    (0, 0),
    window=content_frame,
    anchor="nw"
)


# ============================================================
# SCROLLING
# ============================================================

def update_scroll(event=None):

    canvas.configure(
        scrollregion=canvas.bbox("all")
    )


def resize_content(event):

    canvas.itemconfig(
        canvas_window,
        width=event.width
    )

    update_scroll()


def scroll_up(event=None):

    canvas.yview_scroll(
        -3,
        "units"
    )

    return "break"


def scroll_down(event=None):

    canvas.yview_scroll(
        3,
        "units"
    )

    return "break"


def mouse_wheel(event):

    if event.delta:

        movement = int(-event.delta / 120)

        if movement == 0:

            movement = -1 if event.delta > 0 else 1

        canvas.yview_scroll(
            movement * 3,
            "units"
        )

    return "break"


canvas.bind(
    "<Configure>",
    resize_content
)

content_frame.bind(
    "<Configure>",
    update_scroll
)

window.bind_all(
    "<MouseWheel>",
    mouse_wheel
)

window.bind_all(
    "<Shift-MouseWheel>",
    mouse_wheel
)

window.bind_all(
    "<Button-4>",
    scroll_up
)

window.bind_all(
    "<Button-5>",
    scroll_down
)


# ============================================================
# CLEAR SCREEN
# ============================================================

def clear_screen():

    for widget in content_frame.winfo_children():

        widget.destroy()

    canvas.yview_moveto(0)

    update_scroll()


# ============================================================
# CHOOSE PDF
# ============================================================

def choose_file():

    global selected_file_path

    file = filedialog.askopenfilename(
        title="Select Resume",
        filetypes=[
            ("PDF Files", "*.pdf")
        ]
    )

    if file:

        selected_file_path = file

        file_name.config(
            text="✓ " + file.split("/")[-1],
            fg=GREEN
        )

        analyze_button.config(
            state="normal"
        )


# ============================================================
# ANALYZE RESUME
# ============================================================

def analyze_resume():

    if not selected_file_path:

        messagebox.showwarning(
            "No Resume",
            "Please select a PDF resume first."
        )

        return

    show_loading()

    window.after(
        1200,
        process_resume
    )


# ============================================================
# PROCESS PDF
# ============================================================

def process_resume():

    try:

        reader = PdfReader(
            selected_file_path
        )

        resume_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:

                resume_text += text + "\n"

        if not resume_text.strip():

            messagebox.showerror(
                "PDF Error",
                "No readable text was found in this PDF."
            )

            show_home()

            return

        generate_results(
            resume_text
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            "Could not read the PDF.\n\n"
            + str(error)
        )

        show_home()


# ============================================================
# ANALYZE RESUME TEXT
# ============================================================

def analyze_text(resume_text):

    text = resume_text.lower()

    words = resume_text.split()

    word_count = len(words)


    # --------------------------------------------------------
    # RESUME SECTIONS
    # --------------------------------------------------------

    sections = {

        "Education": [
            "education",
            "academic",
            "qualification"
        ],

        "Experience": [
            "experience",
            "work experience",
            "employment",
            "internship"
        ],

        "Skills": [
            "skills",
            "technical skills",
            "core skills"
        ],

        "Projects": [
            "projects",
            "academic projects",
            "personal projects"
        ],

        "Certifications": [
            "certification",
            "certifications",
            "courses"
        ],

        "LinkedIn": [
            "linkedin.com",
            "linkedin"
        ],

        "GitHub": [
            "github.com",
            "github"
        ]

    }


    # --------------------------------------------------------
    # POINTS
    # --------------------------------------------------------

    points = {

        "Education": 10,
        "Experience": 15,
        "Skills": 10,
        "Projects": 10,
        "Certifications": 5,
        "LinkedIn": 5,
        "GitHub": 5,
        "Contact": 15,
        "Action Verbs": 5,
        "Achievements": 5,
        "Technical Skills": 5,
        "Resume Length": 5

    }


    score = 0

    strengths = []

    weaknesses = []


    # --------------------------------------------------------
    # CHECK SECTIONS
    # --------------------------------------------------------

    section_results = {}


    for section, keywords in sections.items():

        found = any(
            keyword in text
            for keyword in keywords
        )

        section_results[section] = found

        if found:

            score += points[section]


    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    has_email = (
        "@" in text
        and "." in text
    )

    has_phone = any(
        digit in text
        for digit in "0123456789"
    )


    if has_email and has_phone:

        score += points["Contact"]

        strengths.append(
            "Contact information is present."
        )

    else:

        weaknesses.append(
            "Make sure your email and phone number are clearly visible."
        )


    # --------------------------------------------------------
    # ACTION VERBS
    # --------------------------------------------------------

    action_verbs = [

        "built",
        "created",
        "developed",
        "managed",
        "led",
        "designed",
        "implemented",
        "improved",
        "increased",
        "analyzed",
        "optimized",
        "generated",
        "launched",
        "organized",
        "achieved"

    ]


    action_count = sum(
        1
        for verb in action_verbs
        if verb in text
    )


    if action_count >= 3:

        score += points["Action Verbs"]

        strengths.append(
            "Good use of action-oriented language."
        )

    else:

        weaknesses.append(
            "Use more strong action verbs such as built, developed, managed, led and improved."
        )


    # --------------------------------------------------------
    # ACHIEVEMENTS
    # --------------------------------------------------------

    has_numbers = any(
        character.isdigit()
        for character in resume_text
    )


    if has_numbers:

        score += points["Achievements"]

        strengths.append(
            "Resume contains measurable information or numbers."
        )

    else:

        weaknesses.append(
            "Add measurable achievements using numbers, percentages or results."
        )


    # --------------------------------------------------------
    # TECHNICAL SKILLS
    # --------------------------------------------------------

    technical_keywords = [

        "python",
        "sql",
        "java",
        "c++",
        "javascript",
        "html",
        "css",
        "machine learning",
        "data analysis",
        "excel",
        "power bi",
        "tableau",
        "pandas",
        "numpy",
        "git",
        "github",
        "database",
        "api",
        "automation"

    ]


    technical_found = [

        skill
        for skill in technical_keywords
        if skill in text

    ]


    if len(technical_found) >= 2:

        score += points["Technical Skills"]

        strengths.append(
            "Technical skills are clearly represented."
        )

    else:

        weaknesses.append(
            "Add more relevant technical skills and tools."
        )


    # --------------------------------------------------------
    # RESUME LENGTH
    # --------------------------------------------------------

    if 300 <= word_count <= 1000:

        score += points["Resume Length"]

        strengths.append(
            "Resume length is within a reasonable range."
        )

    elif word_count < 300:

        weaknesses.append(
            "Your resume appears too short. Add relevant projects, experience or achievements."
        )

    else:

        weaknesses.append(
            "Your resume may be too long. Remove unnecessary information and keep it concise."
        )


    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    if section_results["Education"]:

        strengths.append(
            "Education section is present."
        )

    else:

        weaknesses.append(
            "Add a clear Education section."
        )


    # --------------------------------------------------------
    # EXPERIENCE
    # --------------------------------------------------------

    if section_results["Experience"]:

        strengths.append(
            "Experience section is present."
        )

    else:

        weaknesses.append(
            "Add internships, work experience or relevant practical experience."
        )


    # --------------------------------------------------------
    # SKILLS
    # --------------------------------------------------------

    if section_results["Skills"]:

        strengths.append(
            "Skills section is present."
        )

    else:

        weaknesses.append(
            "Add a dedicated Skills section."
        )


    # --------------------------------------------------------
    # PROJECTS
    # --------------------------------------------------------

    if section_results["Projects"]:

        strengths.append(
            "Projects section is present."
        )

    else:

        weaknesses.append(
            "Add relevant projects to demonstrate practical skills."
        )


    # --------------------------------------------------------
    # LINKEDIN
    # --------------------------------------------------------

    if section_results["LinkedIn"]:

        strengths.append(
            "LinkedIn profile is included."
        )

    else:

        weaknesses.append(
            "Add your LinkedIn profile."
        )


    # --------------------------------------------------------
    # GITHUB
    # --------------------------------------------------------

    if section_results["GitHub"]:

        strengths.append(
            "GitHub profile is included."
        )

    else:

        weaknesses.append(
            "Add GitHub if you have technical projects."
        )


    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    max_score = sum(
        points.values()
    )

    final_score = round(
        (score / max_score) * 100
    )

    final_score = max(
        0,
        min(
            final_score,
            100
        )
    )


    # --------------------------------------------------------
    # RECRUITER SUMMARY
    # --------------------------------------------------------

    if final_score >= 85:

        summary = (
            "This is a strong resume with good structure and "
            "relevant information. It already has many elements "
            "that recruiters and ATS systems look for."
        )

    elif final_score >= 70:

        summary = (
            "This resume has a good foundation and contains "
            "several important sections. A few improvements "
            "could make it much stronger for recruiters."
        )

    elif final_score >= 50:

        summary = (
            "The resume contains useful information, but it "
            "needs refinement. Improving structure, achievements "
            "and relevant keywords could significantly improve it."
        )

    else:

        summary = (
            "The resume needs significant improvement before "
            "being used for competitive applications. Focus on "
            "structure, relevant skills, experience and measurable achievements."
        )


    return {

        "score": final_score,

        "word_count": word_count,

        "strengths": strengths,

        "weaknesses": weaknesses,

        "summary": summary,

        "technical_skills": technical_found

    }


# ============================================================
# LOADING SCREEN
# ============================================================

def show_loading():

    clear_screen()


    tk.Frame(
        content_frame,
        bg=BG,
        height=100
    ).pack()


    tk.Label(
        content_frame,
        text="REVIEWING YOUR RESUME",
        font=("Arial", 12, "bold"),
        bg=BG,
        fg=GREEN
    ).pack()


    tk.Label(
        content_frame,
        text="Analyzing your resume...",
        font=("Arial", 30, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(
        pady=(15, 10)
    )


    tk.Label(
        content_frame,
        text="HireReady is checking every section.",
        font=("Arial", 13),
        bg=BG,
        fg=MUTED
    ).pack()


    dots_frame = tk.Frame(
        content_frame,
        bg=BG
    )

    dots_frame.pack(
        pady=40
    )


    for i in range(3):

        tk.Label(
            dots_frame,
            text="●",
            font=("Arial", 20),
            bg=BG,
            fg=GREEN
        ).pack(
            side="left",
            padx=8
        )


    tk.Label(
        content_frame,
        text="Checking sections  •  keywords  •  achievements  •  ATS readiness",
        font=("Arial", 10),
        bg=BG,
        fg=MUTED
    ).pack()


    update_scroll()


# ============================================================
# STAT CARD
# ============================================================

def create_stat(parent, value, label):

    card = tk.Frame(
        parent,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.pack(
        side="left",
        expand=True,
        fill="x",
        padx=5
    )


    tk.Label(
        card,
        text=value,
        font=("Arial", 24, "bold"),
        bg=CARD,
        fg=GREEN
    ).pack(
        pady=(18, 2)
    )


    tk.Label(
        card,
        text=label,
        font=("Arial", 9, "bold"),
        bg=CARD,
        fg=MUTED
    ).pack(
        pady=(0, 18)
    )


# ============================================================
# LIST CARD
# ============================================================

def create_list_card(parent, title, items, color):

    card = tk.Frame(
        parent,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.pack(
        fill="x",
        padx=50,
        pady=10
    )


    tk.Label(
        card,
        text=title,
        font=("Arial", 12, "bold"),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=25,
        pady=(22, 12)
    )


    if not items:

        tk.Label(
            card,
            text="No major issues detected.",
            font=("Arial", 10),
            bg=CARD,
            fg=MUTED
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 22)
        )

        return


    for item in items:

        row = tk.Frame(
            card,
            bg=CARD
        )

        row.pack(
            fill="x",
            padx=25,
            pady=5
        )


        tk.Label(
            row,
            text="●",
            font=("Arial", 9),
            bg=CARD,
            fg=color
        ).pack(
            side="left",
            anchor="n",
            pady=2
        )


        tk.Label(
            row,
            text=item,
            font=("Arial", 10),
            bg=CARD,
            fg=TEXT,
            wraplength=800,
            justify="left"
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(10, 0)
        )


    tk.Frame(
        card,
        bg=CARD,
        height=15
    ).pack()


# ============================================================
# TEXT CARD
# ============================================================

def create_text_card(parent, title, text):

    card = tk.Frame(
        parent,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    card.pack(
        fill="x",
        padx=50,
        pady=10
    )


    tk.Label(
        card,
        text=title,
        font=("Arial", 12, "bold"),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=25,
        pady=(22, 12)
    )


    tk.Label(
        card,
        text=text,
        font=("Arial", 11),
        bg=CARD,
        fg=MUTED,
        wraplength=850,
        justify="left"
    ).pack(
        anchor="w",
        padx=25,
        pady=(0, 25)
    )


# ============================================================
# RESULTS PAGE
# ============================================================

def generate_results(resume_text):

    data = analyze_text(
        resume_text
    )

    clear_screen()


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        content_frame,
        bg=BG
    )

    header.pack(
        fill="x",
        padx=50,
        pady=(35, 10)
    )


    tk.Label(
        header,
        text="HIREDREADY",
        font=("Arial", 11, "bold"),
        bg=BG,
        fg=GREEN
    ).pack(
        anchor="w"
    )


    tk.Label(
        header,
        text="Your Resume Results",
        font=("Arial", 32, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(
        anchor="w",
        pady=(8, 0)
    )


    # --------------------------------------------------------
    # SCORE CARD
    # --------------------------------------------------------

    score_card = tk.Frame(
        content_frame,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    score_card.pack(
        fill="x",
        padx=50,
        pady=20
    )


    tk.Label(
        score_card,
        text="RESUME SCORE",
        font=("Arial", 11, "bold"),
        bg=CARD,
        fg=MUTED
    ).pack(
        pady=(25, 5)
    )


    score = data["score"]


    tk.Label(
        score_card,
        text=str(score) + "/100",
        font=("Arial", 52, "bold"),
        bg=CARD,
        fg=GREEN if score >= 70 else RED
    ).pack()


    if score >= 85:

        score_message = "Excellent resume foundation"

    elif score >= 70:

        score_message = "Good resume foundation"

    elif score >= 50:

        score_message = "Needs improvement"

    else:

        score_message = "Needs significant improvement"


    tk.Label(
        score_card,
        text=score_message,
        font=("Arial", 12),
        bg=CARD,
        fg=MUTED
    ).pack(
        pady=(0, 25)
    )


    # --------------------------------------------------------
    # QUICK STATS
    # --------------------------------------------------------

    stats_frame = tk.Frame(
        content_frame,
        bg=BG
    )

    stats_frame.pack(
        fill="x",
        padx=50,
        pady=5
    )


    create_stat(
        stats_frame,
        str(data["word_count"]),
        "WORDS"
    )


    create_stat(
        stats_frame,
        str(len(data["strengths"])),
        "STRENGTHS"
    )


    create_stat(
        stats_frame,
        str(len(data["weaknesses"])),
        "AREAS TO IMPROVE"
    )


    # --------------------------------------------------------
    # STRENGTHS
    # --------------------------------------------------------

    create_list_card(
        content_frame,
        "WHAT'S WORKING",
        data["strengths"],
        GREEN
    )


    # --------------------------------------------------------
    # WEAKNESSES
    # --------------------------------------------------------

    create_list_card(
        content_frame,
        "AREAS TO IMPROVE",
        data["weaknesses"],
        RED
    )


    # --------------------------------------------------------
    # RECRUITER SUMMARY
    # --------------------------------------------------------

    create_text_card(
        content_frame,
        "RECRUITER SUMMARY",
        data["summary"]
    )


    # --------------------------------------------------------
    # IMPROVEMENT TIPS
    # --------------------------------------------------------

    tips = [

        "Use numbers and percentages to show measurable impact.",

        "Start bullet points with strong action verbs.",

        "Tailor your technical skills to the job description.",

        "Keep important information easy for ATS systems to find.",

        "Use clear section headings such as Education, Experience, Skills and Projects.",

        "Remove unnecessary information and keep the resume concise."

    ]


    create_list_card(
        content_frame,
        "IMPROVEMENT TIPS",
        tips,
        GREEN
    )


    # --------------------------------------------------------
    # ANALYZE ANOTHER
    # --------------------------------------------------------

    button_frame = tk.Frame(
        content_frame,
        bg=BG
    )

    button_frame.pack(
        pady=(25, 60)
    )


    tk.Button(
        button_frame,
        text="ANALYZE ANOTHER RESUME",
        font=("Arial", 11, "bold"),
        bg=GREEN,
        fg="white",
        activebackground=GREEN_DARK,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        padx=30,
        pady=13,
        command=show_home
    ).pack()


    update_scroll()


# ============================================================
# HOME PAGE
# ============================================================

def show_home():

    global selected_file_path
    global file_name
    global analyze_button

    selected_file_path = None

    clear_screen()


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    header = tk.Frame(
        content_frame,
        bg=BG
    )

    header.pack(
        fill="x",
        padx=50,
        pady=(40, 20)
    )


    tk.Label(
        header,
        text="HIREDREADY",
        font=("Arial", 11, "bold"),
        bg=BG,
        fg=GREEN
    ).pack(
        anchor="w"
    )


    tk.Label(
        header,
        text="Your resume,\nreviewed.",
        font=("Arial", 38, "bold"),
        bg=BG,
        fg=TEXT,
        justify="left"
    ).pack(
        anchor="w",
        pady=(10, 5)
    )


    tk.Label(
        header,
        text="Get a quick ATS-style review of your resume\n"
             "and understand exactly what you can improve.",
        font=("Arial", 13),
        bg=BG,
        fg=MUTED,
        justify="left"
    ).pack(
        anchor="w"
    )


    # --------------------------------------------------------
    # UPLOAD CARD
    # --------------------------------------------------------

    upload_card = tk.Frame(
        content_frame,
        bg=CARD,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    upload_card.pack(
        fill="x",
        padx=50,
        pady=25
    )


    tk.Label(
        upload_card,
        text="UPLOAD YOUR RESUME",
        font=("Arial", 11, "bold"),
        bg=CARD,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=30,
        pady=(30, 8)
    )


    tk.Label(
        upload_card,
        text="PDF format only",
        font=("Arial", 10),
        bg=CARD,
        fg=MUTED
    ).pack(
        anchor="w",
        padx=30
    )


    # --------------------------------------------------------
    # CHOOSE PDF
    # --------------------------------------------------------

    tk.Button(
        upload_card,
        text="CHOOSE PDF",
        font=("Arial", 11, "bold"),
        bg=GREEN,
        fg="white",
        activebackground=GREEN_DARK,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        padx=25,
        pady=12,
        command=choose_file
    ).pack(
        anchor="w",
        padx=30,
        pady=(20, 10)
    )


    # --------------------------------------------------------
    # FILE NAME
    # --------------------------------------------------------

    file_name = tk.Label(
        upload_card,
        text="No file selected",
        font=("Arial", 10),
        bg=CARD,
        fg=MUTED
    )

    file_name.pack(
        anchor="w",
        padx=30,
        pady=(0, 15)
    )


    # --------------------------------------------------------
    # ANALYZE BUTTON
    # --------------------------------------------------------

    analyze_button = tk.Button(
        upload_card,
        text="ANALYZE RESUME",
        font=("Arial", 11, "bold"),
        bg=GREEN_DARK,
        fg="white",
        activebackground=GREEN,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        padx=25,
        pady=12,
        state="disabled",
        command=analyze_resume
    )

    analyze_button.pack(
        anchor="w",
        padx=30,
        pady=(0, 30)
    )


    # --------------------------------------------------------
    # HOW IT WORKS
    # --------------------------------------------------------

    tk.Label(
        content_frame,
        text="HOW IT WORKS",
        font=("Arial", 11, "bold"),
        bg=BG,
        fg=TEXT
    ).pack(
        anchor="w",
        padx=50,
        pady=(20, 15)
    )


    steps_frame = tk.Frame(
        content_frame,
        bg=BG
    )

    steps_frame.pack(
        fill="x",
        padx=50,
        pady=(0, 50)
    )


    steps = [

        (
            "01",
            "UPLOAD",
            "Upload your resume as a PDF."
        ),

        (
            "02",
            "ANALYZE",
            "HireReady checks your resume."
        ),

        (
            "03",
            "IMPROVE",
            "Get clear improvement suggestions."
        )

    ]


    for number, title, description in steps:

        step = tk.Frame(
            steps_frame,
            bg=BG
        )

        step.pack(
            side="left",
            expand=True,
            fill="x",
            padx=5
        )


        tk.Label(
            step,
            text=number,
            font=("Arial", 24, "bold"),
            bg=BG,
            fg=GREEN
        ).pack(
            anchor="w"
        )


        tk.Label(
            step,
            text=title,
            font=("Arial", 11, "bold"),
            bg=BG,
            fg=TEXT
        ).pack(
            anchor="w",
            pady=(5, 3)
        )


        tk.Label(
            step,
            text=description,
            font=("Arial", 10),
            bg=BG,
            fg=MUTED,
            wraplength=180,
            justify="left"
        ).pack(
            anchor="w"
        )


    update_scroll()


# ============================================================
# START HIREDREADY
# ============================================================

show_home()

window.mainloop()
