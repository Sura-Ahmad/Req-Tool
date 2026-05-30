from fpdf import FPDF, XPos, YPos
import os

def s(text):
    """Sanitise text: replace characters unsupported by Helvetica (latin-1 range)."""
    replacements = {
        '—': '-', '–': '-', '‘': "'", '’': "'",
        '“': '"', '”': '"', '…': '...', ' ': ' ',
        '→': '->', '←': '<-', '•': '*',
    }
    for ch, rep in replacements.items():
        text = text.replace(ch, rep)
    return text.encode('latin-1', errors='replace').decode('latin-1')

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "Project_Analysis_Report.pdf")

BRAND_BLUE   = (30,  90,  160)
BRAND_DARK   = (20,  40,  80)
ACCENT_GREEN = (16, 124,  87)
ACCENT_ORANGE= (200, 100,  20)
LIGHT_GRAY   = (245, 246, 248)
MID_GRAY     = (170, 175, 185)
TEXT_DARK    = (30,  30,  40)
WHITE        = (255, 255, 255)
WARN_RED     = (192,  30,  30)


class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)
        self.set_margins(20, 20, 20)

    def normalize_text(self, text):
        return s(text)

    # ── header / footer ──────────────────────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return
        self.set_fill_color(*BRAND_DARK)
        self.rect(0, 0, 210, 12, "F")
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 8)
        self.set_y(3)
        self.cell(0, 6, "RequirementsSuperTool  |  Project Analysis Report", align="C")
        self.set_text_color(*TEXT_DARK)
        self.ln(10)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_fill_color(*BRAND_DARK)
        self.rect(0, 283, 210, 14, "F")
        self.set_text_color(*MID_GRAY)
        self.set_font("Helvetica", "", 7.5)
        self.set_y(-11)
        self.cell(0, 5, f"Page {self.page_no()}", align="C")
        self.set_text_color(*TEXT_DARK)

    # ── cover page ───────────────────────────────────────────────────────────
    def cover_page(self):
        self.add_page()
        # full dark background strip
        self.set_fill_color(*BRAND_DARK)
        self.rect(0, 0, 210, 297, "F")

        # decorative accent bar
        self.set_fill_color(*BRAND_BLUE)
        self.rect(0, 100, 210, 6, "F")
        self.set_fill_color(*ACCENT_GREEN)
        self.rect(0, 106, 210, 3, "F")

        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 28)
        self.set_xy(20, 125)
        self.cell(170, 12, "RequirementsSuperTool", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_font("Helvetica", "", 16)
        self.set_text_color(*MID_GRAY)
        self.set_x(20)
        self.cell(170, 8, "Comprehensive Project Analysis Report", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.ln(10)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(180, 210, 255)
        details = [
            ("Prepared for", "Sura Ahmed  |  soraahmed196@gmail.com"),
            ("Date",         "May 1, 2026"),
            ("Project",      "AI-Powered SRS Generation Platform"),
            ("Stack",        "FastAPI  +  Next.js  +  Claude AI  +  PostgreSQL"),
        ]
        self.set_y(195)
        for label, value in details:
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(*MID_GRAY)
            self.cell(50, 7, label + ":", align="R")
            self.set_font("Helvetica", "", 10)
            self.set_text_color(210, 230, 255)
            self.cell(0, 7, "  " + value)
            self.ln(7)

        self.set_text_color(*TEXT_DARK)

    # ── section heading ───────────────────────────────────────────────────────
    def section_title(self, number, title):
        self.ln(4)
        self.set_fill_color(*BRAND_BLUE)
        self.rect(20, self.get_y(), 170, 10, "F")
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 13)
        self.cell(0, 10, f"  {number}  {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*TEXT_DARK)
        self.ln(2)

    # ── sub-heading ──────────────────────────────────────────────────────────
    def sub_heading(self, text, color=None):
        self.ln(3)
        c = color or ACCENT_GREEN
        self.set_fill_color(*c)
        self.rect(20, self.get_y(), 3, 7, "F")
        self.set_x(25)
        self.set_text_color(*c)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*TEXT_DARK)
        self.set_font("Helvetica", "", 10)
        self.ln(1)

    # ── body text ────────────────────────────────────────────────────────────
    def body(self, text, indent=0):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*TEXT_DARK)
        self.set_x(20 + indent)
        self.multi_cell(170 - indent, 5.5, text)
        self.ln(1)

    # ── bullet ───────────────────────────────────────────────────────────────
    def bullet(self, text, indent=0):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*TEXT_DARK)
        x = 20 + indent
        self.set_x(x)
        self.set_fill_color(*BRAND_BLUE)
        self.ellipse(x, self.get_y() + 2.2, 2, 2, "F")
        self.set_x(x + 5)
        self.multi_cell(165 - indent, 5.5, text)
        self.ln(0.5)

    # ── code block ───────────────────────────────────────────────────────────
    def code_block(self, code_text):
        self.ln(2)
        lines = code_text.strip().split("\n")
        h = len(lines) * 5 + 6
        self.set_fill_color(30, 35, 50)
        self.rect(20, self.get_y(), 170, h, "F")
        self.set_text_color(140, 220, 140)
        self.set_font("Courier", "", 8.5)
        self.set_y(self.get_y() + 3)
        for line in lines:
            self.set_x(23)
            self.cell(0, 5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*TEXT_DARK)
        self.set_font("Helvetica", "", 10)
        self.ln(3)

    # ── info box ─────────────────────────────────────────────────────────────
    def info_box(self, text, color=None):
        c = color or (230, 240, 255)
        self.ln(2)
        self.set_fill_color(*c)
        self.set_draw_color(*BRAND_BLUE)
        lines = text.strip().split("\n")
        h = len(lines) * 5.5 + 6
        self.rect(20, self.get_y(), 170, h, "FD")
        self.set_text_color(*BRAND_DARK)
        self.set_font("Helvetica", "", 9.5)
        self.set_y(self.get_y() + 3)
        for line in lines:
            self.set_x(24)
            self.cell(0, 5.5, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*TEXT_DARK)
        self.ln(2)

    # ── two-column row ────────────────────────────────────────────────────────
    def two_col(self, label, value, label_w=55):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*BRAND_DARK)
        self.set_x(20)
        self.cell(label_w, 6, label + ":", align="R")
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*TEXT_DARK)
        self.set_x(20 + label_w + 2)
        self.multi_cell(170 - label_w - 2, 6, value)

    # ── table ─────────────────────────────────────────────────────────────────
    def table(self, headers, rows, col_widths=None):
        self.ln(2)
        n = len(headers)
        if not col_widths:
            col_widths = [170 // n] * n

        # header row
        self.set_fill_color(*BRAND_BLUE)
        self.set_text_color(*WHITE)
        self.set_font("Helvetica", "B", 9.5)
        self.set_x(20)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, " " + h, border=0, fill=True)
        self.ln()

        # data rows
        self.set_text_color(*TEXT_DARK)
        self.set_font("Helvetica", "", 9)
        for ri, row in enumerate(rows):
            self.set_fill_color(245, 247, 252) if ri % 2 == 0 else self.set_fill_color(*WHITE)
            self.set_x(20)
            # compute row height
            max_h = 6
            for ci, cell in enumerate(row):
                lines_n = max(1, len(str(cell)) // (col_widths[ci] // 5) + 1)
                max_h = max(max_h, lines_n * 5)
            for ci, cell in enumerate(row):
                self.cell(col_widths[ci], max_h, " " + str(cell), border="B", fill=True)
            self.ln()
        self.set_fill_color(*WHITE)
        self.ln(2)

    # ── page divider ─────────────────────────────────────────────────────────
    def divider(self):
        self.ln(3)
        self.set_draw_color(*MID_GRAY)
        self.set_line_width(0.3)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(4)

    # ── warn box ─────────────────────────────────────────────────────────────
    def warn_box(self, text):
        self.info_box(text, color=(255, 240, 235))


# ─────────────────────────────────────────────────────────────────────────────
# CONTENT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build(pdf: PDF):

    # ── TABLE OF CONTENTS ─────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*BRAND_DARK)
    pdf.cell(0, 12, "Table of Contents", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.divider()
    toc = [
        ("1", "Project Overview & File Directory"),
        ("2", "Architecture, Patterns & SOLID Principles"),
        ("3", "AI Role — Where & How Claude AI Is Used"),
        ("4", "The Quadrant System"),
        ("5", "Improvement Suggestions"),
        ("6", "Database — Tables, Columns, Keys & Relations"),
        ("7", "Sessions — Authentication & Application Sessions"),
    ]
    pdf.set_font("Helvetica", "", 11)
    for num, title in toc:
        pdf.set_x(20)
        pdf.set_text_color(*BRAND_BLUE)
        pdf.cell(12, 8, num + ".")
        pdf.set_text_color(*TEXT_DARK)
        pdf.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    pdf.set_text_color(*TEXT_DARK)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 1 – FILE DIRECTORY
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("1", "Project Overview & File Directory")

    pdf.body(
        "RequirementsSuperTool is an AI-powered Software Requirements Specification (SRS) generation "
        "platform built for Jordanian organisations. Users answer domain-specific questionnaires, optionally "
        "upload supporting documents, and the system uses Claude AI + a Qdrant vector knowledge-base to "
        "generate IEEE-830-compliant SRS documents, use-cases, and quality cross-checks — all in one workflow."
    )
    pdf.ln(2)

    # ── Backend files ──────────────────────────────────────────────────────────
    pdf.sub_heading("Backend Files  (backend/)")

    backend_files = [
        ("app/main.py",
         "FastAPI application entry point. Registers all routers (auth, domain, upload, requirements, "
         "crosscheck, srs, usecases, admin, profile), mounts the /uploads static-files directory, "
         "and configures CORS middleware for http://localhost:3000."),

        ("app/database.py",
         "SQLAlchemy engine creation and session factory. Exposes get_db() — a dependency-injection "
         "generator used by every router to obtain a database session that is automatically closed after "
         "the request."),

        ("app/knowledge_base_loader.py",
         "Bootstraps the Qdrant vector collection 'knowledge_base'. Loads Jordan-specific PDF files "
         "(jordan_health.pdf, jordan_education.pdf, jordan_finance.pdf), chunks each PDF into 500-word "
         "segments, converts chunks to 384-dim embeddings via the all-MiniLM-L6-v2 sentence-transformer "
         "model, and upserts them to Qdrant for semantic retrieval at inference time."),

        ("app/core/config.py",
         "Pydantic BaseSettings class (Settings). Reads all environment variables from .env: "
         "DATABASE_URL, SECRET_KEY, ALGORITHM, token expiry settings, Qdrant credentials, "
         "Anthropic / OpenAI / Gemini API keys, SMTP config, and FRONTEND_URL."),

        ("app/core/security.py",
         "Pure functions for password security and JWT handling: hash_password (bcrypt), "
         "verify_password, create_access_token, create_refresh_token, verify_token. "
         "Tokens are signed with HS256 using the SECRET_KEY from settings."),

        ("app/core/ai.py",
         "Central AI module. Contains: get_knowledge_context() — queries Qdrant for semantically "
         "relevant domain chunks, and generate_requirements() — sends a two-step prompt to Claude "
         "(validation then full generation) and parses FR-/NFR- prefixed lines from the response."),

        ("app/core/pii.py",
         "Microsoft Presidio wrapper. remove_pii() strips personally-identifiable information from "
         "text before it is sent to Claude. has_pii() returns a boolean for detection checks."),

        ("app/core/audit.py",
         "Provides log_login() helper that writes rows to the login_history table with IP, user-agent, "
         "success/failure, and failure reason. Used exclusively by the auth router."),

        ("app/core/email.py",
         "Async SMTP email sender. send_reset_email() composes and dispatches the password-reset "
         "email. Called as a FastAPI BackgroundTask so it never blocks the HTTP response."),

        ("app/core/vector_store.py",
         "Thin wrapper around QdrantClient exposing search operations. Provides an abstraction layer "
         "between the routers and the raw Qdrant SDK."),

        ("app/models/user.py",
         "SQLAlchemy ORM models: User (id, email, password_hash, full_name, role, is_active, "
         "avatar_url, created_at, last_login), RefreshToken (token_hash, expires_at, is_revoked), "
         "PasswordResetToken (token_hash, expires_at, is_used)."),

        ("app/models/domain.py",
         "ORM models: Domain (name, name_ar, country, is_active), Question (domain_id FK, "
         "question_text, question_text_ar, question_order), UserSession (user_id FK, domain_id FK, "
         "country, role, answers JSON, created_at). Defines ProjectRole enum."),

        ("app/models/requirements.py",
         "ORM model: Requirement (session_id FK, code, description, type, is_edited, "
         "created_at, updated_at)."),

        ("app/models/audit.py",
         "ORM models: AuditLog (user_id FK, action, entity_type, entity_id, details JSON, "
         "ip_address, created_at) and LoginHistory (user_id FK, email_attempted, success, "
         "ip_address, user_agent, failure_reason, created_at). Both tables have composite indexes "
         "for efficient querying."),

        ("app/routers/auth.py",
         "Authentication router (/auth). Handles register, login, logout, forgot-password, "
         "reset-password, /me, and /refresh endpoints. Implements token rotation on login, "
         "anti-enumeration on forgot-password, and SHA-256 hashing of refresh/reset tokens before DB storage."),

        ("app/routers/domain.py",
         "Domain & questionnaire router. GET /domains/ filters by country query param; "
         "GET /domains/{id}/questions returns ordered questions; POST /domains/session "
         "creates a UserSession storing serialised answers."),

        ("app/routers/upload.py",
         "Document ingestion router (/input). POST /input/text processes raw text through PII removal. "
         "POST /input/document accepts PDF or DOCX files, extracts text via pdfplumber/python-docx, "
         "applies PII removal, and returns clean text for the frontend to attach to generation requests."),

        ("app/routers/requirements.py",
         "Requirements CRUD router (/requirements). POST /generate calls core/ai.py, persists FR/NFR "
         "rows, returns them. GET /{session_id}/classified returns separated lists. "
         "PUT /{id} allows inline editing with is_edited flag."),

        ("app/routers/crosscheck.py",
         "Quality-assurance router (/crosscheck). Single GET /{session_id} fetches requirements + "
         "user answers + Qdrant domain context, constructs a structured prompt for Claude, parses "
         "the returned JSON array of issues, colour-codes them by type, and returns counts."),

        ("app/routers/srs.py",
         "SRS generation router (/srs). POST /generate builds an IEEE 830 prompt from project metadata "
         "and saved requirements, calls Claude with max_tokens=4000, and returns the full SRS text."),

        ("app/routers/usecases.py",
         "Use-case generation router (/usecases). POST /generate sends functional requirements to "
         "Claude, which responds with a JSON array of structured use-cases "
         "(title, actor, preconditions, main_flow, postconditions)."),

        ("app/routers/admin.py",
         "Admin-only router (/admin). Exposes stats, user management (list, toggle-active), session "
         "listing, full domain/question CRUD, paginated audit logs, login history, and failed-login "
         "analytics. Every endpoint validates the caller has role='admin'."),

        ("app/routers/profile.py",
         "User profile router (/profile). GET /me, PUT /update (name/email), "
         "POST /upload-avatar (saves file to uploads/avatars/), DELETE /avatar, "
         "PUT /change-password (validates current password before allowing change)."),

        ("app/schemas/",
         "Pydantic v2 schema files (auth.py, domain.py, requirements.py, crosscheck.py, srs.py, "
         "usecases.py, admin.py, profile.py). Enforce request validation and shape API responses. "
         "Separate from ORM models following the DTO pattern."),

        ("alembic/versions/*.py",
         "Seven migration files tracking schema evolution: (1) users + refresh_tokens, "
         "(2) domains + questions + user_sessions, (3) role column on user_sessions, "
         "(4) requirements table, (5) password_reset_tokens, "
         "(6) audit_logs + login_history, (7) avatar_url on users."),

        ("requirements.txt",
         "Python dependencies: fastapi, uvicorn, sqlalchemy, psycopg2-binary, alembic, "
         "anthropic, qdrant-client, sentence-transformers, presidio-analyzer, presidio-anonymizer, "
         "pdfplumber, python-docx, pydantic-settings, python-jose, passlib[bcrypt], "
         "python-multipart, aiosmtplib."),
    ]

    for fname, desc in backend_files:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*BRAND_DARK)
        pdf.set_x(20)
        pdf.cell(0, 6, fname, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_x(25)
        pdf.multi_cell(165, 5, desc)
        pdf.ln(1.5)

    # ── Frontend files ─────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.sub_heading("Frontend Files  (frontend/)", color=ACCENT_ORANGE)

    frontend_files = [
        ("app/page.tsx",
         "Root page. Reads auth tokens from localStorage and immediately redirects to /dashboard "
         "(authenticated) or /auth (unauthenticated). Contains no UI of its own."),

        ("app/layout.tsx",
         "Root Next.js layout. Applies global Tailwind CSS and wraps all pages in the shared HTML "
         "shell with font settings."),

        ("app/auth/page.tsx",
         "Authentication page. Renders login and registration forms with toggle between them. "
         "Calls POST /auth/login or /auth/register via api.ts, stores access_token + "
         "refresh_token in localStorage, then redirects to /dashboard."),

        ("app/dashboard/",
         "Main application area. Sub-pages guide the user through the five-step workflow: "
         "(1) choose domain/country/role, (2) answer questionnaire, (3) upload optional document, "
         "(4) generate and edit requirements, (5) export SRS or use-cases."),

        ("lib/api.ts",
         "Centralised Axios instance. Base URL points to http://localhost:8000. An Axios request "
         "interceptor automatically injects the Authorization: Bearer <token> header from "
         "localStorage on every outgoing call. Exports typed wrappers for every backend endpoint."),

        ("lib/generateSRSWord.ts",
         "Client-side Word document builder using the docx npm library. Receives the AI-generated "
         "SRS text or use-cases JSON and converts it into a professional .docx file — complete with "
         "cover page, revision history table, IEEE 830-structured sections, and formatted use-case "
         "tables. Downloaded directly in the browser without a server round-trip."),

        ("package.json",
         "npm dependencies: next 16.2.2, react 19.2.4, typescript 5, tailwindcss 4, axios, "
         "js-cookie, docx. Dev dependencies: eslint, postcss."),

        ("tsconfig.json",
         "TypeScript compiler configuration. Strict mode enabled, path alias @/* mapped to src."),

        ("next.config.ts",
         "Next.js configuration. Enables the app router, sets up image domains and API rewrites "
         "if needed."),
    ]

    for fname, desc in frontend_files:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*BRAND_DARK)
        pdf.set_x(20)
        pdf.cell(0, 6, fname, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_x(25)
        pdf.multi_cell(165, 5, desc)
        pdf.ln(1.5)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 2 – ARCHITECTURE, PATTERNS & SOLID
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("2", "Architecture, Patterns & SOLID Principles")

    pdf.sub_heading("Overall Architecture")
    pdf.body(
        "The project follows a three-tier client-server architecture:\n"
        "  Tier 1 (Presentation)  — Next.js 16 / React 19 SPA served on port 3000.\n"
        "  Tier 2 (Application)   — FastAPI REST API served on port 8000.\n"
        "  Tier 3 (Data)          — PostgreSQL relational DB + Qdrant vector DB."
    )
    pdf.body(
        "The backend further separates concerns into four horizontal layers:\n"
        "  Routers  ->  Schemas (Pydantic)  ->  Core Services  ->  ORM Models"
    )

    pdf.sub_heading("Design Patterns")

    patterns = [
        ("Repository / Active Record",
         "SQLAlchemy ORM models act as Active Records. Queries are written inline in routers "
         "(db.query(User).filter(...)) because the codebase is small — acceptable for this scale.",
         "req = db.query(Requirement).filter(Requirement.session_id == sid).all()"),

        ("Dependency Injection",
         "FastAPI's Depends() system is used for DB session injection on every endpoint. "
         "This decouples request handling from session lifecycle.",
         "def generate(data: Request, db: Session = Depends(get_db)): ..."),

        ("Service Layer",
         "Core business logic (AI calls, PII, email, audit) lives in app/core/* modules, "
         "not in routers. Routers are thin orchestrators.",
         "# In requirements.py router:\nresult = generate_requirements(domain, role, answers)"),

        ("DTO / Schema Separation",
         "Pydantic schemas (app/schemas/) are separate from SQLAlchemy models (app/models/). "
         "Requests are validated by schemas; ORM models handle persistence.",
         "class RegisterRequest(BaseModel):\n    email: str\n    password: str\n    full_name: str"),

        ("RAG — Retrieval-Augmented Generation",
         "Before calling Claude, the system retrieves the top-3 semantically-similar "
         "chunks from Qdrant for the selected domain and injects them into the prompt "
         "as grounding context. This is the core AI architecture pattern.",
         "context = get_knowledge_context(domain, query)\n# context injected into Claude prompt"),

        ("Background Tasks",
         "FastAPI BackgroundTasks runs email delivery asynchronously after the HTTP "
         "response is already sent, preventing latency spikes.",
         "background_tasks.add_task(send_reset_email, email, name, link)"),

        ("Strategy Pattern (Role Instructions)",
         "The role_instructions dict in ai.py is a lightweight strategy pattern — "
         "each role key maps to a different instruction string injected into the prompt, "
         "changing AI behaviour without branching code.",
         'role_instructions = {\n  "product_owner": "Write as high-level business...",\n  "developer":  "Include APIs, data structures..."\n}'),

        ("Factory / Builder (Word Doc)",
         "generateSRSWord.ts acts as a builder: it receives plain text/JSON and constructs "
         "a fully-formatted .docx document using the docx library's fluent builder API.",
         "// frontend/lib/generateSRSWord.ts\nconst doc = new Document({ sections: [...] })"),
    ]

    for name, description, code in patterns:
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(*BRAND_DARK)
        pdf.set_x(20)
        pdf.cell(0, 7, name, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.body(description, indent=5)
        pdf.code_block(code)

    # ── SOLID ──────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.sub_heading("SOLID Principles", color=ACCENT_ORANGE)

    solid = [
        ("S — Single Responsibility Principle",
         "Each module has one job:\n"
         "  app/core/security.py   -> only password + JWT logic\n"
         "  app/core/pii.py        -> only PII detection/removal\n"
         "  app/core/email.py      -> only email dispatch\n"
         "  app/core/ai.py         -> only Claude prompt orchestration\n"
         "No router handles email AND hashing AND AI — each concern is isolated.",
         "# pii.py — does exactly one thing\nanalyzer = AnalyzerEngine()\ndef remove_pii(text: str) -> str:\n    results = analyzer.analyze(text=text, language='en')\n    return anonymizer.anonymize(text, results).text"),

        ("O — Open/Closed Principle",
         "The role_instructions dictionary in ai.py means adding a new role "
         "(e.g. 'tester') requires only a new dict entry — no modification to existing "
         "logic. Similarly, adding a new domain requires only a new DB row + PDF in the "
         "knowledge base, not code changes.",
         '# Adding a new role = one new dict entry, zero code changes\nrole_instructions["tester"] = "Write test-oriented acceptance criteria..."'),

        ("L — Liskov Substitution Principle",
         "Pydantic BaseSettings (Settings class in config.py) can be subclassed for testing "
         "by providing a different .env file (TEST_DATABASE_URL). The rest of the system uses "
         "settings.DATABASE_URL without knowing which env it is running in.",
         "class Settings(BaseSettings):\n    model_config = ConfigDict(env_file='.env')\n    DATABASE_URL: str\n    TEST_DATABASE_URL: str = ''"),

        ("I — Interface Segregation Principle",
         "Pydantic schemas are granular. RegisterRequest does not include admin fields; "
         "AdminUserResponse does not include password_hash. Each schema is the minimal "
         "contract for its use-case.",
         "class RegisterRequest(BaseModel):\n    email: str; password: str; full_name: str\n\nclass AdminUserResponse(BaseModel):\n    id: UUID; email: str; role: str; is_active: bool"),

        ("D — Dependency Inversion Principle",
         "Routers depend on abstractions (the get_db generator, the generate_requirements "
         "function signature) rather than concrete implementations. Swapping from PostgreSQL "
         "to another SQLAlchemy-compatible DB requires changing only database.py.",
         "# Router depends on the abstraction, not the engine\ndef generate(data, db: Session = Depends(get_db)):\n    session = db.query(UserSession).filter(...).first()"),
    ]

    for principle, explanation, code in solid:
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(*BRAND_DARK)
        pdf.set_x(20)
        pdf.cell(0, 7, principle, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.body(explanation, indent=5)
        pdf.code_block(code)
        pdf.ln(1)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 3 – AI ROLE
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("3", "AI Role — Where & How Claude AI Is Used")

    pdf.body(
        "The entire value proposition of the tool is AI-driven. Claude Sonnet (model ID: "
        "claude-sonnet-4-20250514) is called in four distinct features. Below is a deep-dive "
        "into each one."
    )

    ai_features = [
        ("Feature 1: Requirement Generation  (/requirements/generate)",
         "This is the primary AI feature. The workflow is:\n"
         "  Step 1 — VALIDATION: A lightweight 10-token Claude call checks whether the user's "
         "answers match the chosen domain (returns YES/NO). If NO, an error is returned immediately.\n"
         "  Step 2 — GENERATION: A full prompt is built containing: the selected domain, the "
         "user's role-specific instruction, the Q&A answers, any uploaded document text, and the "
         "top-3 Qdrant knowledge-base chunks for that domain. Claude is asked to output FR-X and "
         "NFR-X labelled requirements. Max tokens: 2000.\n"
         "  Step 3 — PARSING: The response is split line-by-line; lines starting with FR- go to "
         "functional[], lines starting with NFR- go to non_functional[].\n"
         "  Step 4 — PERSISTENCE: Each requirement is saved to the requirements table with "
         "session_id, code, description, and type.",
         'prompt = f"""You are an expert requirements engineer for the {domain} domain in Jordan.\n'
         'Role instruction: {role_instruction}\n'
         'Q&A: {answers_text}\n'
         'Domain Knowledge: {knowledge_context}\n'
         '### Functional Requirements\nFR-1: ...\n### Non-Functional Requirements\nNFR-1: ..."""'),

        ("Feature 2: Cross-Check Analysis  (/crosscheck/{session_id})",
         "Claude acts as a senior requirements reviewer. The prompt provides:\n"
         "  - All saved requirements for the session\n"
         "  - The original Q&A answers (as ground truth)\n"
         "  - Top-5 Qdrant knowledge-base chunks as domain rules\n"
         "Claude is instructed to return a strict JSON array of issue objects. Each issue has:\n"
         "  requirement_code, issue_type (ambiguity/duplicate/inconsistency/conflict/unsupported),\n"
         "  issue_detail, conflict_with.\n"
         "The backend then colour-codes each issue for the frontend:\n"
         "  ambiguity=#FFA500, duplicate=#FF6B6B, inconsistency=#9B59B6,\n"
         "  conflict=#FF0000, unsupported=#3498DB. Max tokens: 1000.",
         '# Colour map applied server-side before returning\ncolor_map = {\n  "ambiguity": "#FFA500",\n  "conflict": "#FF0000",\n  "unsupported": "#3498DB"\n}'),

        ("Feature 3: SRS Document Generation  (/srs/generate)",
         "Claude receives the project name, description, domain, and all saved requirements, "
         "and is instructed to produce a full IEEE 830-standard SRS document with sections:\n"
         "  1. Introduction (Purpose, Scope, Definitions, References, Overview)\n"
         "  2. Overall Description (Perspective, Functions, User Classes, Environment, Constraints)\n"
         "  3. Specific Requirements (Functional, Non-Functional)\n"
         "  4. Appendices\n"
         "The raw text is returned to the frontend, where generateSRSWord.ts converts it to "
         "a downloadable .docx file. Max tokens: 4000.",
         'prompt = f"""Generate a complete IEEE 830 SRS document.\nProject: {project_name}\nDomain: {domain}\nFR: {fr_text}\nNFR: {nfr_text}"""'),

        ("Feature 4: Use-Case Generation  (/usecases/generate)",
         "Claude receives the functional requirements and is asked to return a JSON array of "
         "structured use-case objects. Each object includes:\n"
         "  title, actor, preconditions, main_flow (numbered steps as text), postconditions.\n"
         "The frontend converts this JSON into formatted use-case tables in the .docx export. "
         "Max tokens: 3000.",
         '# Claude returns pure JSON — no markdown code fences in ideal case\n[\n  {\n    "title": "User Login",\n    "actor": "Registered User",\n    "preconditions": "User has account",\n    "main_flow": "1. Open login\\n2. Enter creds",\n    "postconditions": "User authenticated"\n  }\n]'),

        ("Supporting AI Infrastructure: Knowledge Base (Qdrant + Sentence Transformers)",
         "Before any Claude call, relevant domain knowledge is retrieved via semantic search:\n"
         "  1. knowledge_base_loader.py reads domain PDFs (Health, Education, Finance for Jordan).\n"
         "  2. Text is chunked into 500-word segments.\n"
         "  3. Each chunk is embedded using the all-MiniLM-L6-v2 sentence-transformer (384 dims).\n"
         "  4. Embeddings are stored in Qdrant with metadata: {text, domain, country, source}.\n"
         "  5. At inference time, get_knowledge_context() embeds the query and performs cosine "
         "similarity search filtered by domain, returning the top-3 most relevant chunks.",
         "model = SentenceTransformer('all-MiniLM-L6-v2')\ndef text_to_embedding(text: str) -> list:\n    return model.encode(text).tolist()\n\n# Cosine similarity search in Qdrant\nresults = qdrant_client.query_points(\n    collection_name='knowledge_base',\n    query=embedding,\n    query_filter={'must': [{'key': 'domain', 'match': {'value': domain}}]},\n    limit=3\n).points"),
    ]

    for title, explanation, code in ai_features:
        pdf.set_font("Helvetica", "B", 10.5)
        pdf.set_text_color(*BRAND_DARK)
        pdf.set_x(20)
        pdf.cell(0, 7, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.body(explanation, indent=5)
        pdf.code_block(code)
        pdf.ln(2)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 4 – QUADRANT
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("4", "The Quadrant System")

    pdf.body(
        "The 'quadrant' in this project is the four-role stakeholder classification system. "
        "Every requirements-generation session is tied to one of four project roles, and the AI "
        "produces a completely different output for each. Think of it as a 2x2 matrix:"
    )

    pdf.ln(3)
    # Draw the quadrant visually
    left = 30
    top  = pdf.get_y()
    w, h = 70, 40

    quad_data = [
        ("Product Owner",       BRAND_BLUE,   "Business outcomes\nUser stories\nWHAT not HOW"),
        ("Business Analyst",    ACCENT_GREEN, "Functional specs\nAcceptance criteria\nMeasurable"),
        ("Developer",           (80, 60, 160),"Technical specs\nAPIs & data structures\nPerformance"),
        ("Stakeholder",         ACCENT_ORANGE,"Business goals\nROI & impact\nNon-technical"),
    ]
    positions = [(left, top), (left + w + 5, top), (left, top + h + 5), (left + w + 5, top + h + 5)]
    labels = ["Strategic / Business", "Operational / Functional", "Technical / Implementation", "Executive / Value"]

    for i, ((qname, color, desc), (x, y)) in enumerate(zip(quad_data, positions)):
        pdf.set_fill_color(*color)
        pdf.rect(x, y, w, h, "F")
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_xy(x + 2, y + 3)
        pdf.cell(w - 4, 6, qname, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 8)
        for line in desc.split("\n"):
            pdf.set_x(x + 4)
            pdf.cell(w - 6, 5, "* " + line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(top + 2 * h + 20)
    pdf.set_text_color(*TEXT_DARK)

    pdf.sub_heading("How It Works — Step by Step")
    pdf.body(
        "1. Domain Selection: The user picks a domain (Health, Education, Finance) and a country "
        "(currently Jordan). This determines which knowledge-base chunks will be used.\n\n"
        "2. Role Selection: The user picks their project role — the quadrant position. This selects "
        "the role-specific instruction string injected into the Claude prompt.\n\n"
        "3. Questionnaire: The user answers domain-specific questions (stored in the questions table "
        "for that domain). Answers are serialised as JSON and stored in user_sessions.answers.\n\n"
        "4. Session Creation: A UserSession row is created linking the user, domain, role, and answers.\n\n"
        "5. Requirements Generation: The session_id is passed to /requirements/generate. The AI reads "
        "the role and applies the matching instruction, producing requirements calibrated to that "
        "stakeholder perspective.\n\n"
        "6. Output Differentiation Example:\n"
        "   Same input: 'E-commerce checkout system'\n"
        "   Product Owner output:  'FR-1: System shall allow users to complete purchases in < 3 clicks'\n"
        "   Developer output:      'FR-1: System shall expose a POST /orders REST API accepting "
        "CartItemDTO[], returning OrderID with HTTP 201'\n"
        "   Stakeholder output:    'FR-1: System shall reduce cart abandonment by enabling one-click reorder'"
    )

    pdf.sub_heading("Why This Matters")
    pdf.body(
        "Traditional requirements tools produce one generic output. This quadrant system produces "
        "four specialised views of the same project, each valid and useful for a different audience. "
        "The AI acts as a translator between business intent and technical specification — the role "
        "label is the translation instruction."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 5 – IMPROVEMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("5", "Improvement Suggestions")

    improvements = [
        ("1. Rate Limiting on AI Endpoints",
         "HIGH PRIORITY",
         "Currently there is no rate limiting on /requirements/generate, /srs/generate, or "
         "/crosscheck. A single user could trigger thousands of Claude API calls, incurring huge "
         "costs. Add slowapi or a Redis-backed token bucket (e.g. 10 requests/minute/user) on "
         "all Claude-calling endpoints.",
         WARN_RED),

        ("2. Cloud Avatar Storage",
         "MEDIUM",
         "Avatars are saved to the local filesystem (uploads/avatars/). This breaks in any "
         "multi-instance or containerised deployment. Migrate to an S3-compatible object store "
         "(AWS S3, MinIO, Cloudflare R2) and store only the URL in the DB.",
         ACCENT_ORANGE),

        ("3. Centralise Error Handling",
         "MEDIUM",
         "Many try/except blocks silently swallow exceptions (e.g., in crosscheck.py the JSON "
         "parse failure returns []) making debugging difficult. Add a global FastAPI "
         "exception_handler and structured logging (structlog or python-json-logger) so every "
         "error has a correlation ID.",
         ACCENT_ORANGE),

        ("4. Prompt Caching",
         "MEDIUM",
         "The knowledge-base context and role instructions are static. Use Anthropic's prompt "
         "caching feature (cache_control: {type: 'ephemeral'}) on the system/knowledge sections "
         "to reduce token cost by up to 90% on repeated calls for the same domain.",
         ACCENT_GREEN),

        ("5. Test Coverage",
         "HIGH PRIORITY",
         "No test files were found (only .pytest_cache metadata). Add: unit tests for "
         "security.py (hashing, JWT), integration tests for auth flow, and mocked tests for "
         "AI endpoints using pytest + httpx + unittest.mock. Aim for > 70% coverage.",
         WARN_RED),

        ("6. Hardcoded Knowledge Base Paths",
         "LOW",
         "knowledge_base_loader.py hardcodes filenames (jordan_health.pdf, jordan_education.pdf, "
         "jordan_finance.pdf). Move to a config-driven or DB-driven approach so admins can upload "
         "new domain PDFs through the admin dashboard without code changes.",
         ACCENT_GREEN),

        ("7. Refresh Token Rotation",
         "MEDIUM",
         "On /auth/refresh, the old refresh token is returned unchanged. Implement rotation: "
         "revoke the old token and issue a new one on every refresh. This limits the damage "
         "window if a refresh token is stolen.",
         ACCENT_ORANGE),

        ("8. Arabic Language Support in AI Prompts",
         "LOW",
         "The domain and question tables have Arabic name/question columns, but all Claude prompts "
         "are English-only. Add a language parameter to generation requests and provide "
         "bilingual prompt templates so Arabic-speaking users receive Arabic requirements.",
         ACCENT_GREEN),

        ("9. Requirement Versioning",
         "LOW",
         "When a requirement is edited (is_edited=True), the original AI-generated text is "
         "overwritten. Add a requirement_history table to track changes with timestamps and "
         "user IDs so auditors can see what was changed from the AI baseline.",
         ACCENT_GREEN),

        ("10. HTTPS & Production CORS",
         "HIGH PRIORITY",
         "CORS is configured for http://localhost:3000 only. Before any production deployment, "
         "configure HTTPS (TLS termination at a reverse proxy), set CORS to the actual production "
         "domain, and move SECRET_KEY and API keys to a secrets manager (AWS Secrets Manager, "
         "HashiCorp Vault).",
         WARN_RED),
    ]

    for title, priority, description, color in improvements:
        pdf.set_fill_color(*color)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_x(20)
        pdf.cell(130, 7, "  " + title, fill=True)
        pdf.cell(40, 7, priority, fill=True, align="C")
        pdf.ln()
        pdf.set_text_color(*TEXT_DARK)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_x(25)
        pdf.multi_cell(165, 5.5, description)
        pdf.ln(3)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 6 – DATABASE
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("6", "Database — Tables, Columns, Keys & Relations")

    pdf.body(
        "The database is PostgreSQL, managed via SQLAlchemy ORM and Alembic migrations. "
        "There are 9 tables in total. All primary keys are UUID (v4) generated by the application "
        "layer (uuid.uuid4()), not database-generated sequences — giving globally unique IDs "
        "that are safe to expose in URLs."
    )

    # --- users ---
    pdf.sub_heading("Table: users")
    pdf.table(
        ["Column", "Type", "Constraints", "Notes"],
        [
            ["id",            "UUID",          "PK, NOT NULL",              "Auto-generated uuid4"],
            ["email",         "VARCHAR(255)",   "UNIQUE, NOT NULL, INDEX",   "Login identifier"],
            ["password_hash", "VARCHAR(255)",   "NOT NULL",                  "BCrypt hash"],
            ["full_name",     "VARCHAR(100)",   "NOT NULL",                  ""],
            ["role",          "ENUM",           "DEFAULT 'user'",            "user | admin"],
            ["is_active",     "BOOLEAN",        "DEFAULT TRUE",              "Soft disable"],
            ["avatar_url",    "VARCHAR(500)",   "NULLABLE",                  "Local file path"],
            ["created_at",    "DATETIME",       "DEFAULT utcnow",            ""],
            ["last_login",    "DATETIME",       "NULLABLE",                  "Updated on login"],
        ],
        col_widths=[38, 35, 45, 52]
    )

    # --- refresh_tokens ---
    pdf.sub_heading("Table: refresh_tokens")
    pdf.table(
        ["Column", "Type", "Constraints", "Notes"],
        [
            ["id",          "UUID",         "PK",                    ""],
            ["user_id",     "UUID",         "NOT NULL",              "Implicit FK -> users.id"],
            ["token_hash",  "VARCHAR(255)", "UNIQUE, NOT NULL",      "SHA-256 of the JWT"],
            ["expires_at",  "DATETIME",     "NOT NULL",              "7 days from issue"],
            ["is_revoked",  "BOOLEAN",      "DEFAULT FALSE",         "Set True on logout"],
        ],
        col_widths=[38, 35, 45, 52]
    )

    # --- password_reset_tokens ---
    pdf.sub_heading("Table: password_reset_tokens")
    pdf.table(
        ["Column", "Type", "Constraints", "Notes"],
        [
            ["id",          "UUID",         "PK",               ""],
            ["user_id",     "UUID",         "NOT NULL",         "Implicit FK -> users.id"],
            ["token_hash",  "VARCHAR(255)", "UNIQUE, NOT NULL", "SHA-256 of urlsafe token"],
            ["expires_at",  "DATETIME",     "NOT NULL",         "1 hour from issue"],
            ["is_used",     "BOOLEAN",      "DEFAULT FALSE",    "One-time use flag"],
            ["created_at",  "DATETIME",     "DEFAULT utcnow",   ""],
        ],
        col_widths=[38, 35, 45, 52]
    )

    # --- domains ---
    pdf.add_page()
    pdf.sub_heading("Table: domains")
    pdf.table(
        ["Column", "Type", "Constraints", "Notes"],
        [
            ["id",         "UUID",          "PK",            ""],
            ["name",       "VARCHAR(100)",  "NOT NULL",      "English name e.g. Health"],
            ["name_ar",    "VARCHAR(100)",  "NOT NULL",      "Arabic name"],
            ["country",    "VARCHAR(10)",   "NOT NULL",      "ISO code e.g. JO"],
            ["is_active",  "BOOLEAN",       "DEFAULT TRUE",  "Soft delete flag"],
            ["created_at", "DATETIME",      "DEFAULT utcnow",""],
        ],
        col_widths=[38, 35, 45, 52]
    )

    # --- questions ---
    pdf.sub_heading("Table: questions")
    pdf.table(
        ["Column", "Type", "Constraints", "Notes"],
        [
            ["id",               "UUID",         "PK",                        ""],
            ["domain_id",        "UUID",         "FK -> domains.id, NOT NULL","Owning domain"],
            ["question_text",    "TEXT",         "NOT NULL",                  "English"],
            ["question_text_ar", "TEXT",         "NOT NULL",                  "Arabic"],
            ["question_order",   "VARCHAR(10)",  "NOT NULL",                  "Display order"],
            ["is_active",        "BOOLEAN",      "DEFAULT TRUE",              "Soft delete"],
        ],
        col_widths=[38, 35, 45, 52]
    )

    # --- user_sessions ---
    pdf.sub_heading("Table: user_sessions")
    pdf.table(
        ["Column", "Type", "Constraints", "Notes"],
        [
            ["id",         "UUID",         "PK",                         ""],
            ["user_id",    "UUID",         "FK -> users.id, NOT NULL",   "Owner"],
            ["domain_id",  "UUID",         "FK -> domains.id, NOT NULL", "Selected domain"],
            ["country",    "VARCHAR(10)",  "NOT NULL",                   "e.g. JO"],
            ["role",       "VARCHAR(50)",  "NOT NULL, DEFAULT 'business_analyst'","Quadrant role"],
            ["answers",    "TEXT",         "NULLABLE",                   "JSON serialised Q&A"],
            ["created_at", "DATETIME",     "DEFAULT utcnow",             ""],
        ],
        col_widths=[38, 35, 45, 52]
    )

    # --- requirements ---
    pdf.sub_heading("Table: requirements")
    pdf.table(
        ["Column", "Type", "Constraints", "Notes"],
        [
            ["id",          "UUID",         "PK",                               ""],
            ["session_id",  "UUID",         "FK -> user_sessions.id, NOT NULL", "Parent session"],
            ["code",        "VARCHAR(20)",  "NOT NULL",                         "FR-1, NFR-2 ..."],
            ["description", "TEXT",         "NOT NULL",                         "AI or edited text"],
            ["type",        "VARCHAR(20)",  "NOT NULL",                         "functional | non_functional"],
            ["is_edited",   "BOOLEAN",      "DEFAULT FALSE",                    "User-modified flag"],
            ["created_at",  "DATETIME",     "DEFAULT utcnow",                   ""],
            ["updated_at",  "DATETIME",     "DEFAULT utcnow",                   "Updated on PUT"],
        ],
        col_widths=[38, 35, 45, 52]
    )

    # --- audit_logs ---
    pdf.add_page()
    pdf.sub_heading("Table: audit_logs")
    pdf.table(
        ["Column", "Type", "Constraints", "Notes"],
        [
            ["id",          "UUID",         "PK",                                   ""],
            ["user_id",     "UUID",         "FK -> users.id ON DELETE SET NULL",    "Nullable (anonymous)"],
            ["action",      "VARCHAR(100)", "NOT NULL",                             "e.g. domain_created"],
            ["entity_type", "VARCHAR(50)",  "NOT NULL",                             "domain, user, question"],
            ["entity_id",   "VARCHAR(255)", "NULLABLE",                             "UUID of affected row"],
            ["details",     "JSON",         "NULLABLE",                             "Arbitrary metadata"],
            ["ip_address",  "VARCHAR(45)",  "NULLABLE",                             "IPv4/IPv6"],
            ["created_at",  "DATETIME",     "DEFAULT utcnow, INDEX",                ""],
        ],
        col_widths=[38, 35, 45, 52]
    )
    pdf.body("Indexes: ix_audit_logs_user_id, ix_audit_logs_created_at, ix_audit_logs_action")

    # --- login_history ---
    pdf.sub_heading("Table: login_history")
    pdf.table(
        ["Column", "Type", "Constraints", "Notes"],
        [
            ["id",               "UUID",          "PK",                                 ""],
            ["user_id",          "UUID",          "FK -> users.id ON DELETE SET NULL",  "Nullable"],
            ["email_attempted",  "VARCHAR(255)",  "NOT NULL, INDEX",                    "Attempted email"],
            ["success",          "BOOLEAN",       "NOT NULL",                           ""],
            ["ip_address",       "VARCHAR(45)",   "NULLABLE",                           ""],
            ["user_agent",       "VARCHAR(500)",  "NULLABLE",                           "Browser string"],
            ["failure_reason",   "VARCHAR(50)",   "NULLABLE",                           "user_not_found | wrong_password | account_disabled"],
            ["created_at",       "DATETIME",      "DEFAULT utcnow, INDEX",              ""],
        ],
        col_widths=[38, 35, 45, 52]
    )
    pdf.body("Indexes: ix_login_history_email, ix_login_history_created_at, ix_login_history_user_id")

    # --- ER relations summary ---
    pdf.sub_heading("Entity Relationships (ER Summary)")
    pdf.info_box(
        "users  (1) ----< (N)  refresh_tokens        [user_id]\n"
        "users  (1) ----< (N)  password_reset_tokens [user_id]\n"
        "users  (1) ----< (N)  user_sessions         [user_id]\n"
        "users  (1) ----< (N)  audit_logs            [user_id, ON DELETE SET NULL]\n"
        "users  (1) ----< (N)  login_history         [user_id, ON DELETE SET NULL]\n"
        "domains(1) ----< (N)  questions             [domain_id]\n"
        "domains(1) ----< (N)  user_sessions         [domain_id]\n"
        "user_sessions(1) ---< (N) requirements      [session_id]"
    )

    pdf.sub_heading("Notable Database Design Decisions")
    decisions = [
        "UUIDs as PKs: Prevents enumeration attacks and simplifies multi-instance inserts.",
        "SHA-256 token hashing: Refresh/reset tokens stored as hashes — even if the DB is compromised, tokens cannot be replayed without the original string.",
        "ON DELETE SET NULL on audit/login FKs: Deleting a user preserves audit history — user_id becomes NULL but the log entry survives.",
        "Soft deletes (is_active): Domains and questions are never hard-deleted; is_active=False hides them from users but preserves historical data.",
        "answers as TEXT (JSON): Flexible — no schema migration needed when question sets change. Trade-off: no SQL-level querying of individual answers.",
        "No explicit SQLAlchemy relationship() declarations: FK constraints exist in migrations, but ORM relationships are not declared — queries join manually. Simple but limits lazy-loading conveniences.",
    ]
    for d in decisions:
        pdf.bullet(d)

    # ═══════════════════════════════════════════════════════════════════════════
    # SECTION 7 – SESSIONS
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_title("7", "Sessions — Authentication & Application Sessions")

    pdf.body(
        "The project uses two distinct concepts both called 'session', which is important to distinguish:"
    )

    pdf.sub_heading("Type A: JWT Authentication Sessions")
    pdf.body(
        "This is the standard HTTP authentication mechanism. It consists of two tokens:"
    )

    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(*BRAND_DARK)
    pdf.set_x(20)
    pdf.cell(0, 7, "A1 — Access Token (Short-lived JWT)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body(
        "Created by create_access_token() in security.py. Signed with HS256 using SECRET_KEY. "
        "Payload: {'sub': user_id, 'exp': utcnow + ACCESS_TOKEN_EXPIRE_MINUTES}. "
        "Lifetime configured in .env (typically 15-60 minutes). "
        "NOT stored in the database — stateless. "
        "Sent in every API request as: Authorization: Bearer <token>. "
        "Verified by verify_token() which decodes the JWT and checks expiry.",
        indent=5
    )
    pdf.code_block(
        "def create_access_token(data: dict) -> str:\n"
        "    to_encode = data.copy()\n"
        "    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)\n"
        "    to_encode.update({'exp': expire})\n"
        "    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)"
    )

    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(*BRAND_DARK)
    pdf.set_x(20)
    pdf.cell(0, 7, "A2 — Refresh Token (Long-lived JWT, DB-backed)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.body(
        "Created by create_refresh_token(). Same structure as access token but with a longer "
        "lifetime (configured as REFRESH_TOKEN_EXPIRE_DAYS, typically 7 days). "
        "The raw JWT is returned to the frontend (stored in localStorage). "
        "The SHA-256 hash of the token is stored in the refresh_tokens table. "
        "On /auth/refresh, the backend: (1) decodes the JWT to check signature/expiry, "
        "(2) computes SHA-256 hash and looks it up in DB, (3) checks is_revoked=False, "
        "(4) issues a new access token. "
        "On /auth/logout, the hash is found and is_revoked is set to True.",
        indent=5
    )
    pdf.code_block(
        "# On logout — revoke the refresh token\ntoken_hash = hashlib.sha256(data.refresh_token.encode()).hexdigest()\n"
        "db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()\n"
        "if db_token:\n    db_token.is_revoked = True\n    db.commit()"
    )

    pdf.sub_heading("A3 — Password Reset Token (One-Time Use)")
    pdf.body(
        "Generated with secrets.token_urlsafe(32) — a cryptographically secure random URL-safe string. "
        "The SHA-256 hash is stored in password_reset_tokens with:\n"
        "  expires_at = utcnow + 1 hour\n"
        "  is_used = False\n"
        "The raw token is embedded in the reset link emailed to the user. "
        "On use: the hash is looked up, expiry checked, is_used set True, and password updated. "
        "Anti-enumeration: the forgot-password endpoint always returns the same message regardless "
        "of whether the email exists.",
        indent=5
    )

    pdf.sub_heading("Frontend Token Storage")
    pdf.body(
        "Tokens are stored in browser localStorage (not HttpOnly cookies). This is a common "
        "React/SPA pattern but has a security trade-off: localStorage is accessible to JavaScript, "
        "so XSS vulnerabilities could expose tokens. For higher security, migrate to HttpOnly "
        "cookie storage with SameSite=Strict."
    )
    pdf.info_box(
        "Security note: The current localStorage approach is acceptable for development/MVP.\n"
        "For production with sensitive data, consider HttpOnly cookies + CSRF tokens instead."
    )

    pdf.sub_heading("Type B: Application / Questionnaire Sessions  (user_sessions table)")
    pdf.body(
        "This is a completely separate concept from authentication. A 'user session' here represents "
        "one requirements-generation workflow — a snapshot of a user's choices at a point in time."
    )
    pdf.body(
        "When a user completes the questionnaire and clicks 'Generate Requirements', a POST to "
        "/domains/session creates a user_sessions row containing:\n"
        "  - user_id:   who started this session\n"
        "  - domain_id: which domain was selected (Health, Education, Finance)\n"
        "  - country:   typically 'JO' for Jordan\n"
        "  - role:      the quadrant role (product_owner, business_analyst, developer, stakeholder)\n"
        "  - answers:   JSON string of [{question_id, answer}, ...]\n"
        "  - created_at: timestamp\n\n"
        "This session_id is then the primary key linking all downstream data: requirements, "
        "cross-check results, SRS generation, and use-case generation all query by session_id."
    )

    pdf.sub_heading("Session Lifecycle Diagram")
    pdf.info_box(
        "User Answers Questionnaire\n"
        "        |\n"
        "        v\n"
        "POST /domains/session  ->  user_sessions row created  ->  session_id returned\n"
        "        |\n"
        "        +---> POST /requirements/generate (session_id)  ->  requirements rows saved\n"
        "        |                                                    |\n"
        "        +---> GET  /crosscheck/{session_id}             <---+  (reads requirements)\n"
        "        |\n"
        "        +---> POST /srs/generate (session_id)           <---+  (reads requirements)\n"
        "        |\n"
        "        +---> POST /usecases/generate (session_id)      <---+  (reads FR requirements)"
    )

    pdf.sub_heading("Summary: Two Types of Session Compared")
    pdf.table(
        ["Attribute", "Auth Session (JWT)", "App Session (user_sessions)"],
        [
            ["Purpose",       "Authenticate API calls",       "Track requirements workflow"],
            ["Storage",       "localStorage (client) + DB hash",  "PostgreSQL table"],
            ["Lifetime",      "15min access / 7day refresh",  "Permanent (no expiry)"],
            ["Created at",    "Login / Register",             "Questionnaire completion"],
            ["Invalidation",  "Logout (revoke) or expiry",    "Never deleted (historical record)"],
            ["Key field",     "JWT 'sub' claim = user UUID",  "session_id UUID"],
        ],
        col_widths=[38, 65, 67]
    )

    # ── final page ────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(*BRAND_DARK)
    pdf.rect(0, 100, 210, 2, "F")
    pdf.set_fill_color(*BRAND_BLUE)
    pdf.rect(0, 102, 210, 1, "F")
    pdf.set_y(120)
    pdf.set_text_color(*BRAND_DARK)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "End of Report", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*MID_GRAY)
    pdf.cell(0, 8, "RequirementsSuperTool  |  Project Analysis  |  May 2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(*TEXT_DARK)
    pdf.multi_cell(0, 6,
        "This document was auto-generated by analysing the full source code of the project, "
        "including all backend Python modules, SQLAlchemy models, Alembic migrations, FastAPI "
        "routers, Pydantic schemas, and Next.js/TypeScript frontend files.",
        align="C"
    )


def main():
    pdf = PDF()
    pdf.cover_page()
    build(pdf)
    pdf.output(OUTPUT_PATH)
    print(f"PDF saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
