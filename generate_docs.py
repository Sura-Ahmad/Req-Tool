"""
Requirements Super Tool - Project Documentation Generator
Generates a comprehensive PDF for supervisor review.
Run: python generate_docs.py
Output: project_documentation.pdf
"""

import sys
import os

# Allow running from project root without activating venv manually
venv_site_packages = os.path.join(os.path.dirname(__file__), "backend", ".venv", "Lib", "site-packages")
if os.path.isdir(venv_site_packages):
    sys.path.insert(0, venv_site_packages)

from fpdf import FPDF

# ─────────────────────────────────────────────
# PDF Helper Class
# ─────────────────────────────────────────────

class DocPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, "Requirements Super Tool - Technical Documentation", align="L")
        self.ln(0)
        self.set_draw_color(230, 230, 230)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 6, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def title_page(self):
        self.add_page()
        self.set_fill_color(30, 42, 74)
        self.rect(0, 0, self.w, 80, "F")
        self.set_y(22)
        self.set_font("Helvetica", "B", 28)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "Requirements Super Tool", align="C", ln=True)
        self.set_font("Helvetica", "", 14)
        self.set_text_color(255, 107, 107)
        self.cell(0, 8, "Complete Technical Documentation", align="C", ln=True)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, "Prepared for Supervisor Review  |  May 2026", align="C", ln=True)

        self.set_text_color(0, 0, 0)
        self.set_y(100)
        self.set_font("Helvetica", "B", 11)
        toc = [
            ("1", "Project Overview"),
            ("2", "Technology Stack"),
            ("3", "Authentication & Session Mechanism"),
            ("4", "System Architecture"),
            ("5", "Design Patterns"),
            ("6", "Database - Tables & Relationships"),
            ("7", "Libraries & Their Purpose"),
            ("8", "How to Add a New Domain / Module"),
            ("9", "Where Does Implementation Start?"),
            ("10", "Complete API Route Reference"),
        ]
        self.cell(0, 8, "Table of Contents", ln=True)
        self.set_font("Helvetica", "", 10)
        for num, title in toc:
            self.set_fill_color(248, 249, 250) if int(num) % 2 == 0 else self.set_fill_color(255, 255, 255)
            self.cell(14, 7, num + ".", fill=True)
            self.cell(0, 7, title, fill=True, ln=True)

    def section(self, num, title):
        self.add_page()
        self.set_fill_color(30, 42, 74)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 11, f"  Section {num}: {title}", fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def sub(self, title):
        self.ln(3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 42, 74)
        self.set_fill_color(240, 244, 255)
        self.cell(0, 8, f"  {title}", fill=True, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def bullet(self, items, indent=6):
        self.set_font("Helvetica", "", 10)
        usable = self.w - self.l_margin - self.r_margin - indent - 4
        for item in items:
            self.set_x(self.l_margin + indent)
            self.cell(4, 5.5, chr(149))
            self.multi_cell(usable, 5.5, item)
        self.ln(1)

    def code(self, lines):
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.3)
        x0 = self.get_x()
        y0 = self.get_y()
        h = len(lines) * 4.8 + 4
        self.rect(x0, y0, self.w - self.l_margin - self.r_margin, h, "FD")
        self.set_xy(x0 + 2, y0 + 2)
        for line in lines:
            self.cell(0, 4.8, line, ln=True)
        self.ln(3)
        self.set_line_width(0.2)
        self.set_draw_color(0, 0, 0)

    def table(self, headers, rows, col_widths=None):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(30, 42, 74)
        self.set_text_color(255, 255, 255)
        usable = self.w - self.l_margin - self.r_margin
        if col_widths is None:
            col_widths = [usable / len(headers)] * len(headers)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 9)
        self.set_text_color(0, 0, 0)
        for ri, row in enumerate(rows):
            self.set_fill_color(248, 249, 250) if ri % 2 == 0 else self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6, str(cell), border=1, fill=True)
            self.ln()
        self.ln(2)

    def label(self, text):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(255, 107, 107)
        self.cell(0, 6, text, ln=True)
        self.set_text_color(0, 0, 0)


# ─────────────────────────────────────────────
# Section 1 - Overview
# ─────────────────────────────────────────────

def section1_overview(pdf):
    pdf.section("1", "Project Overview")
    pdf.body(
        "The Requirements Super Tool is an AI-powered requirements elicitation and management system. "
        "Its primary purpose is to help software teams generate, classify, validate, and export software "
        "requirements using Large Language Models (Claude by Anthropic). "
        "It reduces the time and expertise needed to write high-quality functional and non-functional requirements."
    )
    pdf.sub("Target Users")
    pdf.bullet([
        "Business Analysts  - primary users who gather and document requirements",
        "Product Owners     - define scope and prioritise features",
        "Developers         - contribute technical constraints and NFRs",
        "Stakeholders       - provide domain context and answer questionnaires",
    ])
    pdf.sub("Core Capabilities")
    pdf.bullet([
        "Multi-step guided wizard: domain -> role -> questions -> input -> generate",
        "AI-powered functional and non-functional requirement generation",
        "Requirements cross-check for conflicts and inconsistencies",
        "IEEE 830 SRS document generation (PDF and Word export)",
        "Use case generation from requirements",
        "Knowledge base (PDF upload) to give domain-specific context to the AI",
        "Admin panel: user management, audit logs, login history, domain/question CRUD",
        "PII (Personally Identifiable Information) detection and masking on input text",
        "Full requirement edit history with audit trail",
    ])
    pdf.sub("Supported Domains (Seeded for Jordan)")
    pdf.bullet([
        "Health       - medical/clinical systems",
        "Education    - learning management systems",
        "Finance      - banking/financial systems",
    ])
    pdf.body(
        "New domains can be added by an administrator through the admin panel or API "
        "without any code changes."
    )


# ─────────────────────────────────────────────
# Section 2 - Stack
# ─────────────────────────────────────────────

def section2_stack(pdf):
    pdf.section("2", "Technology Stack")

    pdf.sub("Backend")
    pdf.table(
        ["Technology", "Version", "Purpose"],
        [
            ["Python 3", "3.10+", "Core backend language"],
            ["FastAPI", "0.135.2", "REST API framework (async, auto OpenAPI docs)"],
            ["SQLAlchemy", "2.0+", "ORM for PostgreSQL database access"],
            ["Alembic", "1.18.4", "Database schema migration management"],
            ["Uvicorn", "0.42.0", "ASGI server to run FastAPI"],
            ["Pydantic", "2.12.5", "Request/response data validation and serialisation"],
            ["pydantic-settings", "2.13.1", "Type-safe config from .env files"],
            ["psycopg2-binary", "2.9.11", "PostgreSQL database driver"],
        ],
        [52, 28, 100]
    )

    pdf.sub("Frontend")
    pdf.table(
        ["Technology", "Version", "Purpose"],
        [
            ["Next.js", "16.2.2", "React meta-framework (App Router, SSR, file routing)"],
            ["React", "19.2.4", "UI component library"],
            ["TypeScript", "5", "Type-safe JavaScript"],
            ["Tailwind CSS", "4", "Utility-first CSS framework"],
            ["Axios", "1.14.0", "HTTP client for REST API calls"],
            ["Lucide React", "1.7.0", "Icon library"],
        ],
        [42, 22, 116]
    )

    pdf.sub("Databases")
    pdf.table(
        ["Database", "Type", "Purpose"],
        [
            ["PostgreSQL", "Relational (SQL)", "Primary data store: users, sessions, requirements"],
            ["Qdrant", "Vector database", "Stores PDF knowledge base embeddings for semantic search"],
        ],
        [40, 40, 100]
    )

    pdf.sub("Languages Per Layer")
    pdf.table(
        ["Layer", "Language"],
        [
            ["Backend API", "Python 3"],
            ["Frontend UI", "TypeScript / TSX (React JSX)"],
            ["Styling", "CSS (via Tailwind utility classes)"],
            ["Primary Database", "SQL (PostgreSQL dialect via SQLAlchemy)"],
            ["Migrations", "Python (Alembic migration scripts)"],
            ["Configuration", "TOML/INI (alembic.ini), JSON (tsconfig, package.json)"],
        ],
        [60, 120]
    )


# ─────────────────────────────────────────────
# Section 3 - Auth
# ─────────────────────────────────────────────

def section3_auth(pdf):
    pdf.section("3", "Authentication & Session Mechanism")

    pdf.sub("Type: JWT with Refresh Token Rotation (Stateless)")
    pdf.body(
        "The system uses JSON Web Tokens (JWT) - a stateless authentication mechanism. "
        "Two tokens are issued at login: a short-lived Access Token and a long-lived Refresh Token. "
        "There is NO traditional server-side session table. The JWT carries the user identity. "
        "Only the refresh token HASH is persisted in the database for revocation tracking."
    )

    pdf.sub("Token Details")
    pdf.table(
        ["Token", "Expiry", "Storage", "Algorithm"],
        [
            ["Access Token", "~15 minutes", "Browser localStorage", "HS256 (HMAC-SHA256)"],
            ["Refresh Token", "7 days", "Database (SHA-256 hash only)", "HS256"],
        ],
        [38, 32, 60, 50]
    )

    pdf.sub("Complete Authentication Flow")
    pdf.code([
        "STEP 1 - REGISTER / LOGIN",
        "  Client  ->  POST /auth/login  { email, password }",
        "  Server validates password with bcrypt",
        "  Server creates:  access_token  (JWT, 15 min)",
        "                   refresh_token (JWT, 7 days)",
        "  Server stores SHA-256(refresh_token) in 'refresh_tokens' table",
        "  Server returns both tokens to client",
        "",
        "STEP 2 - AUTHENTICATED REQUEST",
        "  Client reads access_token from localStorage",
        "  Client sends:  Authorization: Bearer <access_token>",
        "  Server verifies JWT signature and expiry",
        "  Server extracts user_id from token payload -> request proceeds",
        "",
        "STEP 3 - TOKEN REFRESH (when access_token expires -> 401)",
        "  Axios interceptor catches the 401 Unauthorized response",
        "  Client sends:  POST /auth/refresh  { refresh_token }",
        "  Server hashes received token, looks up hash in DB",
        "  Server checks: not revoked, not expired",
        "  TOKEN ROTATION: old refresh_token.is_revoked = True",
        "  Server issues NEW access_token + NEW refresh_token",
        "  Queued failed requests are retried with new access_token",
        "",
        "STEP 4 - LOGOUT",
        "  Client sends:  POST /auth/logout  { refresh_token }",
        "  Server sets refresh_token.is_revoked = True in DB",
        "  Client clears localStorage (removes both tokens)",
    ])

    pdf.sub("Security Features")
    pdf.bullet([
        "Passwords hashed with bcrypt (passlib) - never stored in plaintext",
        "Refresh tokens stored as SHA-256 hashes - plaintext never touches DB",
        "Token rotation: every refresh issues a new pair and revokes the old",
        "All login attempts (success and failure) logged to login_history table",
        "Failed login reason stored: wrong_password / user_not_found / account_disabled",
        "Rate limiting: 10 req/min on generation, 5/min on SRS (SlowAPI)",
    ])

    pdf.sub("Relevant Files")
    pdf.table(
        ["File", "Responsibility"],
        [
            ["backend/app/core/security.py", "create_access_token(), create_refresh_token(), verify_token()"],
            ["backend/app/routers/auth.py", "Login, register, logout, refresh, forgot/reset password"],
            ["backend/app/models/user.py", "RefreshToken and PasswordResetToken SQLAlchemy models"],
            ["frontend/lib/api.ts", "Axios interceptor: attaches Bearer, handles 401, queues retries"],
        ],
        [75, 105]
    )

    pdf.sub("Password Reset Flow")
    pdf.code([
        "POST /auth/forgot-password  { email }",
        "  -> Server generates secure random token",
        "  -> Stores SHA-256 hash in 'password_reset_tokens' (expires 1 hour)",
        "  -> Sends email async (BackgroundTasks - non-blocking)",
        "",
        "POST /auth/reset-password  { token, new_password }",
        "  -> Server verifies token hash, checks not used / not expired",
        "  -> Updates user.password_hash with new bcrypt hash",
        "  -> Marks token.is_used = True (one-time use)",
    ])


# ─────────────────────────────────────────────
# Section 4 - Architecture
# ─────────────────────────────────────────────

def section4_architecture(pdf):
    pdf.section("4", "System Architecture")

    pdf.sub("Architecture Style: Layered (N-Tier) Architecture")
    pdf.body(
        "Each layer has a single responsibility and only depends on the layer below it. "
        "This separation makes the system testable, maintainable, and extensible."
    )

    pdf.code([
        "==========================================================",
        "  PRESENTATION LAYER  (Frontend)",
        "  Next.js 16 / React 19 / TypeScript / Tailwind CSS 4",
        "  Pages: Auth, Wizard, Requirements, Profile, Admin",
        "==========================================================",
        "              | HTTP REST (JSON via Axios + Bearer token)",
        "              v",
        "==========================================================",
        "  API LAYER  (FastAPI Routers)",
        "  /auth  /domains  /requirements  /crosscheck  /srs",
        "  /usecases  /admin  /profile  /input",
        "  SlowAPI rate limiting  |  CORSMiddleware",
        "==========================================================",
        "              | Depends() injection",
        "              v",
        "==========================================================",
        "  BUSINESS LOGIC / CORE SERVICES",
        "  core/ai.py       - Claude AI integration",
        "  core/security.py - JWT token management",
        "  core/audit.py    - Audit trail logging",
        "  core/email.py    - Async SMTP email",
        "  core/pii.py      - PII detection / masking",
        "==========================================================",
        "         |                        |",
        "  SQLAlchemy ORM            HTTP clients",
        "         v                        v",
        "  [PostgreSQL]            [Qdrant (vector DB)]",
        "  10 tables               Knowledge base embeddings",
        "                                  |",
        "                     [Anthropic Claude API]",
        "                      claude-sonnet-4",
    ])

    pdf.sub("Request Lifecycle: Generate Requirements")
    pdf.code([
        "1. User completes wizard -> clicks 'Generate Requirements'",
        "2. Frontend: POST /requirements/generate  (with Bearer token)",
        "   Payload: { session_id, country, domain, role, answers, text }",
        "",
        "3. API Layer (requirements.py):",
        "   a. SlowAPI checks rate limit: max 10 req/min per IP",
        "   b. verify_token() extracts user from JWT",
        "   c. get_db() injects SQLAlchemy session via Depends()",
        "",
        "4. Business Logic (core/ai.py):",
        "   a. Selects prompt template based on user role (Strategy pattern)",
        "   b. Queries Qdrant for relevant domain knowledge (semantic search)",
        "   c. Calls Anthropic Claude API:",
        "      - System prompt with prompt caching (reduces cost)",
        "      - User context: domain, role, answers, project description",
        "      - Injected domain knowledge from vector search",
        "   d. Parses AI response into structured requirements list",
        "",
        "5. Data Layer (SQLAlchemy):",
        "   a. Saves requirements to 'requirements' table",
        "   b. Links each requirement to the user_session",
        "",
        "6. Audit (core/audit.py):",
        "   a. Logs action to 'audit_logs' table",
        "",
        "7. Response: JSON list returned to frontend",
        "8. Frontend renders tabbed view: FR / NFR / Use Cases / SRS",
    ])

    pdf.sub("Frontend Structure (Next.js App Router)")
    pdf.code([
        "frontend/app/",
        "  layout.tsx                    <- Root: fonts, metadata",
        "  page.tsx                      <- Entry: redirect /auth or /dashboard",
        "  auth/page.tsx                 <- Login / Register / Forgot Password",
        "  auth/reset-password/page.tsx  <- Password reset form",
        "  dashboard/",
        "    layout.tsx                  <- Sidebar nav: Wizard, Requirements, Profile",
        "    wizard/page.tsx             <- 5-step guided wizard",
        "    requirements/page.tsx       <- FR / NFR / Use Cases / SRS tabs",
        "    profile/page.tsx            <- View and edit profile",
        "    admin/",
        "      layout.tsx               <- Admin sidebar navigation",
        "      page.tsx                 <- Stats dashboard",
        "      users/page.tsx           <- User management",
        "      sessions/page.tsx        <- Session viewer",
        "      domains/page.tsx         <- Domain & question CRUD",
        "      knowledge-base/page.tsx  <- PDF upload and management",
        "      audit-log/page.tsx       <- Audit trail",
        "      login-history/page.tsx   <- Failed login monitoring",
        "frontend/lib/",
        "  api.ts                       <- Axios client + all API helpers",
        "  generateSRSWord.ts           <- Word (docx) generation",
    ])


# ─────────────────────────────────────────────
# Section 5 - Patterns
# ─────────────────────────────────────────────

def section5_patterns(pdf):
    pdf.section("5", "Design Patterns")

    pdf.body(
        "Seven design patterns are used in the codebase. "
        "Each entry below includes the pattern name, where it appears, a code example, and its benefit."
    )

    pdf.label("1. Dependency Injection")
    pdf.body("FastAPI's Depends() mechanism injects dependencies (DB session, current user) at runtime.")
    pdf.code([
        "# backend/app/routers/requirements.py",
        "def generate(",
        "    request: Request,",
        "    data: GenerateRequirementsRequest,",
        "    db: Session = Depends(get_db),           # DB session injected",
        "    current_user = Depends(get_current_user) # User injected",
        "):",
        "    ...",
        "",
        "# backend/app/database.py",
        "def get_db():",
        "    db = SessionLocal()",
        "    try:",
        "        yield db",
        "    finally:",
        "        db.close()   # always closes, even on error",
    ])
    pdf.body("Benefit: Route handlers are testable in isolation; infrastructure is swappable without touching business logic.")

    pdf.label("2. Repository Pattern (implicit via ORM)")
    pdf.body("SQLAlchemy Session abstracts all raw SQL. Routes never write SQL strings.")
    pdf.code([
        "# backend/app/routers/admin.py",
        "users = db.query(User).filter(User.is_active == True).all()",
        "user  = db.query(User).filter(User.id == user_id).first()",
        "db.add(new_domain)",
        "db.commit()",
        "db.refresh(new_domain)",
    ])
    pdf.body("Benefit: Switching from PostgreSQL to another database only requires a connection string change.")

    pdf.label("3. Factory Pattern")
    pdf.body("Factory functions create JWT tokens with consistent, centralised configuration.")
    pdf.code([
        "# backend/app/core/security.py",
        "def create_access_token(data: dict) -> str:",
        "    to_encode = data.copy()",
        "    expire = datetime.utcnow() + timedelta(",
        "        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES",
        "    )",
        "    to_encode.update({'exp': expire})",
        "    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm='HS256')",
        "",
        "def create_refresh_token(data: dict) -> str:",
        "    # Same pattern, 7-day expiry",
        "    ...",
    ])
    pdf.body("Benefit: Token format changes happen in one place. All callers get the updated behaviour automatically.")

    pdf.label("4. Strategy Pattern")
    pdf.body("Different AI prompt strategies are selected based on the user's role at runtime.")
    pdf.code([
        "# backend/app/core/ai.py",
        "_ROLE_INSTRUCTIONS = {",
        "    'product_owner':    'Focus on business value and user stories...',",
        "    'business_analyst': 'Focus on detailed functional requirements...',",
        "    'developer':        'Focus on technical constraints and NFRs...',",
        "    'stakeholder':      'Focus on high-level goals and outcomes...',",
        "}",
        "",
        "# Strategy selected at runtime:",
        "instructions = _ROLE_INSTRUCTIONS.get(user_role, default_instructions)",
    ])
    pdf.body("Benefit: Adding a new role requires adding one dictionary entry. No if/elif chains to modify.")

    pdf.label("5. Decorator Pattern")
    pdf.body("Rate limiting is applied non-intrusively via decorators on individual endpoints.")
    pdf.code([
        "# backend/app/routers/requirements.py",
        "@router.post('/generate')",
        "@limiter.limit('10/minute')   # <- rate limiting added without touching handler logic",
        "async def generate(request: Request, data: ..., db: ...):",
        "    ...",
        "",
        "# backend/app/routers/srs.py",
        "@router.post('/generate')",
        "@limiter.limit('5/minute')   # SRS is expensive -> stricter limit",
        "async def generate_srs(...):",
        "    ...",
    ])
    pdf.body("Benefit: Rate limiting logic is centralised in SlowAPI. Endpoints declare their limit declaratively.")

    pdf.label("6. Middleware Pattern")
    pdf.body("Cross-cutting concerns (CORS, rate limiting, error handling) are applied as middleware stacks.")
    pdf.code([
        "# backend/app/main.py",
        "app = FastAPI(title='Requirements AI', version='1.0.0')",
        "",
        "app.state.limiter = limiter",
        "app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)",
        "",
        "app.add_middleware(",
        "    CORSMiddleware,",
        "    allow_origins=[settings.FRONTEND_URL],",
        "    allow_credentials=True,",
        "    allow_methods=['*'],",
        "    allow_headers=['*'],",
        ")",
        "",
        "@app.exception_handler(Exception)",
        "async def global_exception_handler(request, exc):",
        "    correlation_id = str(uuid.uuid4())",
        "    # logs error with unique ID for debugging",
        "    ...",
    ])
    pdf.body("Benefit: Every request automatically passes through CORS and rate limiting without per-route boilerplate.")

    pdf.label("7. Observer Pattern (Background Tasks)")
    pdf.body("Email sending is decoupled from the HTTP response using FastAPI BackgroundTasks.")
    pdf.code([
        "# backend/app/routers/auth.py",
        "from fastapi import BackgroundTasks",
        "",
        "@router.post('/forgot-password')",
        "async def forgot_password(",
        "    data: ForgotPasswordRequest,",
        "    background_tasks: BackgroundTasks,",
        "    db: Session = Depends(get_db)",
        "):",
        "    ...",
        "    # Email sent asynchronously - HTTP response returns immediately",
        "    background_tasks.add_task(send_reset_email, email, reset_link)",
        "    return {'message': 'If email exists, reset link was sent'}",
    ])
    pdf.body("Benefit: HTTP response is not blocked by email delivery. If SMTP fails, the API still responds successfully.")


# ─────────────────────────────────────────────
# Section 6 - Database
# ─────────────────────────────────────────────

def section6_database(pdf):
    pdf.section("6", "Database - Tables & Relationships")

    pdf.sub("Overview")
    pdf.bullet([
        "Database engine: PostgreSQL",
        "ORM: SQLAlchemy 2.0 (declarative models)",
        "Migrations: Alembic (9 migration versions applied in order)",
        "All primary keys: UUID (not integer auto-increment)",
        "All datetimes: UTC (datetime.utcnow as column default)",
        "Total tables: 10",
    ])

    tables_data = [
        ("users", "Core user accounts and authentication",
         [("id","UUID","PK, auto-generated"),
          ("email","String(255)","UNIQUE, INDEXED, NOT NULL"),
          ("password_hash","String(255)","bcrypt hash, NOT NULL"),
          ("full_name","String(100)","NOT NULL"),
          ("role","Enum","'user' or 'admin', DEFAULT 'user'"),
          ("is_active","Boolean","DEFAULT True"),
          ("created_at","DateTime","DEFAULT utcnow"),
          ("last_login","DateTime","NULLABLE"),
         ]),
        ("refresh_tokens", "JWT refresh token store (hashed)",
         [("id","UUID","PK"),
          ("user_id","UUID","FK -> users.id"),
          ("token_hash","String(255)","SHA-256 hash, UNIQUE"),
          ("expires_at","DateTime","NOT NULL"),
          ("is_revoked","Boolean","DEFAULT False"),
         ]),
        ("password_reset_tokens", "One-time password reset tokens sent via email",
         [("id","UUID","PK"),
          ("user_id","UUID","FK -> users.id ON DELETE CASCADE"),
          ("token_hash","String(255)","UNIQUE, INDEXED"),
          ("expires_at","DateTime","1-hour expiry"),
          ("is_used","Boolean","DEFAULT False - prevents token reuse"),
          ("created_at","DateTime","DEFAULT utcnow"),
         ]),
        ("domains", "Business domains for requirements gathering",
         [("id","UUID","PK"),
          ("name","String(100)","English name (e.g. 'Health')"),
          ("name_ar","String(100)","Arabic name"),
          ("country","String(10)","Country code e.g. 'JO'"),
          ("is_active","Boolean","Soft-delete flag"),
          ("created_at","DateTime","DEFAULT utcnow"),
         ]),
        ("questions", "Domain-specific questionnaire questions",
         [("id","UUID","PK"),
          ("domain_id","UUID","FK -> domains.id"),
          ("question_text","Text","English question"),
          ("question_text_ar","Text","Arabic question"),
          ("question_order","String(10)","Display order within domain"),
          ("is_active","Boolean","Soft-delete flag"),
         ]),
        ("user_sessions", "Wizard session: domain + role + user answers",
         [("id","UUID","PK"),
          ("user_id","UUID","FK -> users.id"),
          ("domain_id","UUID","FK -> domains.id"),
          ("country","String(10)","Country context"),
          ("role","String(50)","product_owner|business_analyst|developer|stakeholder"),
          ("answers","Text","JSON string of answers to domain questions"),
          ("created_at","DateTime","DEFAULT utcnow"),
         ]),
        ("requirements", "Generated requirements linked to a session",
         [("id","UUID","PK"),
          ("session_id","UUID","FK -> user_sessions.id"),
          ("code","String(20)","e.g. 'FR-001', 'NFR-003'"),
          ("description","Text","The requirement text"),
          ("type","String(20)","'functional' or 'non_functional'"),
          ("is_edited","Boolean","True if user has modified it after generation"),
          ("created_at","DateTime","DEFAULT utcnow"),
          ("updated_at","DateTime","Updated on each edit"),
         ]),
        ("requirement_history", "Full audit trail of requirement edits",
         [("id","UUID","PK"),
          ("requirement_id","UUID","FK -> requirements.id, INDEXED"),
          ("old_description","Text","Requirement text before the edit"),
          ("changed_at","DateTime","DEFAULT utcnow"),
         ]),
        ("audit_logs", "System-wide action audit log",
         [("id","UUID","PK"),
          ("user_id","UUID","FK -> users.id ON DELETE SET NULL, NULLABLE"),
          ("action","String(100)","Action type INDEXED e.g. CREATE, UPDATE, DELETE"),
          ("entity_type","String(50)","Affected entity type e.g. 'requirement', 'domain'"),
          ("entity_id","String(255)","ID of the affected entity"),
          ("details","JSON","Extra context: old value, new value, etc."),
          ("ip_address","String(45)","Requester IP"),
          ("created_at","DateTime","DEFAULT utcnow, INDEXED"),
         ]),
        ("login_history", "Login attempt log for security monitoring",
         [("id","UUID","PK"),
          ("user_id","UUID","FK -> users.id ON DELETE SET NULL, NULLABLE"),
          ("email_attempted","String(255)","Email used in attempt, INDEXED"),
          ("success","Boolean","True = successful login"),
          ("ip_address","String(45)","Login attempt IP address"),
          ("user_agent","String(500)","Browser / client information"),
          ("failure_reason","String(50)","wrong_password / user_not_found / account_disabled"),
          ("created_at","DateTime","DEFAULT utcnow, INDEXED"),
         ]),
    ]

    for tname, tdesc, cols in tables_data:
        pdf.label(f"Table: {tname}")
        pdf.body(f"Purpose: {tdesc}")
        pdf.table(["Column","Type","Notes"], cols, [45, 32, 103])

    pdf.add_page()
    pdf.sub("Entity Relationship Diagram (ERD)")
    pdf.code([
        "users (1) ---------------------------- (*) refresh_tokens",
        "  |",
        "  +-- (1) -- CASCADE DELETE ---------- (*) password_reset_tokens",
        "  |",
        "  +-- (1) -- SET NULL ---------------- (*) audit_logs",
        "  |",
        "  +-- (1) -- SET NULL ---------------- (*) login_history",
        "  |",
        "  +-- (1) ----------------------------- (*) user_sessions",
        "                |",
        "                +-- domain_id --> (1) domains",
        "                |                      |",
        "                |                      +--- (1) --- (*) questions",
        "                |",
        "                +----------------------- (*) requirements",
        "                                               |",
        "                                               +--- (1) --- (*) requirement_history",
    ])

    pdf.sub("All Relationships")
    pdf.table(
        ["From Table", "To Table", "Type", "On Delete"],
        [
            ["users","refresh_tokens","One-to-Many","(implicit)"],
            ["users","password_reset_tokens","One-to-Many","CASCADE"],
            ["users","audit_logs","One-to-Many","SET NULL"],
            ["users","login_history","One-to-Many","SET NULL"],
            ["users","user_sessions","One-to-Many","(implicit)"],
            ["domains","questions","One-to-Many","(implicit)"],
            ["domains","user_sessions","One-to-Many","(implicit)"],
            ["user_sessions","requirements","One-to-Many","(implicit)"],
            ["requirements","requirement_history","One-to-Many","(implicit)"],
        ],
        [42, 50, 32, 56]
    )

    pdf.sub("Alembic Migration History (9 versions)")
    pdf.table(
        ["Migration ID", "Description", "Date"],
        [
            ["71d1c5b8c2a9","Create users and refresh_tokens tables","2026-04-01"],
            ["09bcdf56bc88","Add domains, questions, user_sessions tables","2026-04-01"],
            ["569fded45c94","Add role column to user_sessions","2026-04-01"],
            ["a9d0817cac7b","Add requirements table","2026-04-05"],
            ["b3c1e2f4a5d6","Add password_reset_tokens table","2026-04-27"],
            ["c4d2e3f1a8b9","Add audit_logs and login_history tables","2026-04-29"],
            ["d5e3f2a1b6c8","Add avatar_url to users","2026-04-29"],
            ["e6f4a3b2c9d1","Drop avatar_url from users","2026-05-01"],
            ["f7a5d3b8e2c4","Add requirement_history table","2026-05-01"],
        ],
        [42, 90, 28]
    )


# ─────────────────────────────────────────────
# Section 7 - Libraries
# ─────────────────────────────────────────────

def section7_libraries(pdf):
    pdf.section("7", "Libraries & Their Purpose")

    pdf.sub("Backend Libraries (Python)")
    pdf.table(
        ["Library", "Version", "Purpose"],
        [
            ["FastAPI","0.135.2","REST API framework with auto docs, async support, and validation"],
            ["SQLAlchemy",">=2.0","ORM: maps Python classes to database tables, abstracts SQL"],
            ["Alembic","1.18.4","Database migration tool: version-controls schema changes"],
            ["Pydantic","2.12.5","Data validation: ensures correct types for all requests/responses"],
            ["pydantic-settings","2.13.1","Loads typed configuration from .env files"],
            ["Uvicorn","0.42.0","ASGI server: runs FastAPI app in development and production"],
            ["psycopg2-binary","2.9.11","Low-level PostgreSQL driver used internally by SQLAlchemy"],
            ["python-jose[cryptography]","3.5.0","JWT encode/decode and signature verification"],
            ["passlib[bcrypt]","1.7.4","Password hashing with bcrypt - never stores plaintext"],
            ["anthropic","0.89.0","Official Anthropic SDK to call Claude AI API"],
            ["qdrant-client","1.17.1","Client to connect to Qdrant vector database"],
            ["sentence-transformers","5.4.1","Converts text to vector embeddings (all-MiniLM-L6-v2)"],
            ["pdfplumber","0.11.9","Extracts text from uploaded PDF files for knowledge base"],
            ["fpdf2",">=2.8.7","Generates PDF documents (SRS export, this documentation file)"],
            ["python-docx","1.2.0","Generates Word .docx documents (SRS export)"],
            ["slowapi","0.1.9","Rate limiting middleware for FastAPI"],
            ["aiosmtplib",">=2.0","Async SMTP: sends password reset emails without blocking"],
            ["presidio-analyzer","latest","Microsoft PII detection: finds sensitive data in input text"],
            ["presidio-anonymizer","latest","Microsoft PII masking: replaces sensitive data with tokens"],
        ],
        [52, 22, 106]
    )

    pdf.sub("Frontend Libraries (JavaScript / TypeScript)")
    pdf.table(
        ["Library", "Version", "Purpose"],
        [
            ["Next.js","16.2.2","React framework: file-based routing, layouts, SSR, build tool"],
            ["React","19.2.4","UI component library - all pages are React functional components"],
            ["TypeScript","5","Type system for JavaScript - catches type errors at compile time"],
            ["Tailwind CSS","4","Utility CSS: style elements with class names directly in JSX"],
            ["Axios","1.14.0","HTTP client: makes REST API calls, handles request interceptors"],
            ["Lucide React","1.7.0","Icon library (LayoutDashboard, FileText, User, Shield, etc.)"],
            ["js-cookie","3.0.5","Cookie read/write helper"],
            ["docx","9.6.1","Client-side Word document generation for SRS Word export"],
            ["file-saver","2.0.5","Triggers browser file download for PDF/Word exports"],
        ],
        [42, 22, 116]
    )

    pdf.sub("AI & Vector Search Pipeline")
    pdf.body(
        "1. Admin uploads domain PDF files via the knowledge base admin panel. "
        "2. pdfplumber extracts the full text from each PDF. "
        "3. sentence-transformers splits text into 500-word chunks and generates 384-dimensional embeddings "
        "   using the all-MiniLM-L6-v2 model. "
        "4. qdrant-client stores these vectors in Qdrant with domain and country metadata filters. "
        "5. At requirement generation time, the user's project description is also embedded. "
        "6. Qdrant performs semantic (vector) search to retrieve the top-K most relevant knowledge chunks. "
        "7. These chunks are injected into Claude's prompt as domain context. "
        "8. The anthropic SDK calls Claude Sonnet 4 with prompt caching on the system prompt "
        "   (reduces API costs by caching repeated context)."
    )


# ─────────────────────────────────────────────
# Section 8 - Add New Domain
# ─────────────────────────────────────────────

def section8_add_domain(pdf):
    pdf.section("8", "How to Add a New Domain / Module")

    pdf.sub("Option A: Add a New Business Domain (no code needed)")
    pdf.body("Business domains (Health, Education, Finance) can be added from the Admin UI without any code changes:")
    pdf.code([
        "1. Login as admin user",
        "2. Navigate to /dashboard/admin/domains",
        "3. Click 'Add Domain'",
        "4. Enter: name (English), name_ar (Arabic), country code (e.g. 'JO')",
        "5. Add questions for the domain (English + Arabic)",
        "6. Optionally upload PDFs to knowledge base for AI context",
        "",
        "OR via API:",
        "POST /admin/domains",
        "Authorization: Bearer <admin_token>",
        "{ 'name': 'Agriculture', 'name_ar': 'Alz-r-a-ah', 'country': 'JO' }",
    ])

    pdf.sub("Option B: Add a New Backend Feature Module")
    pdf.body("Follow these 5 steps to add a new backend feature (example: 'Reports'):")

    pdf.label("Step 1 - Create the Router File")
    pdf.code([
        "# File: backend/app/routers/reports.py",
        "from fastapi import APIRouter, Depends",
        "from sqlalchemy.orm import Session",
        "from app.database import get_db",
        "from app.core.security import get_current_user",
        "",
        "router = APIRouter(prefix='/reports', tags=['Reports'])",
        "",
        "@router.get('/')",
        "def list_reports(db: Session = Depends(get_db),",
        "                 user = Depends(get_current_user)):",
        "    return db.query(Report).filter(Report.user_id == user.id).all()",
    ])

    pdf.label("Step 2 - Create Pydantic Schemas")
    pdf.code([
        "# File: backend/app/schemas/reports.py",
        "from pydantic import BaseModel",
        "from typing import Optional",
        "",
        "class ReportCreate(BaseModel):",
        "    title: str",
        "    description: Optional[str] = None",
        "",
        "class ReportResponse(BaseModel):",
        "    id: str",
        "    title: str",
        "    class Config:",
        "        from_attributes = True",
    ])

    pdf.label("Step 3 - Create SQLAlchemy Model")
    pdf.code([
        "# File: backend/app/models/reports.py",
        "from sqlalchemy import Column, String, DateTime, ForeignKey",
        "from app.database import Base",
        "import uuid",
        "from datetime import datetime",
        "",
        "class Report(Base):",
        "    __tablename__ = 'reports'",
        "    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))",
        "    title = Column(String(200), nullable=False)",
        "    user_id = Column(String, ForeignKey('users.id'), nullable=False)",
        "    created_at = Column(DateTime, default=datetime.utcnow)",
    ])

    pdf.label("Step 4 - Register Router in main.py")
    pdf.code([
        "# File: backend/app/main.py",
        "from app.routers import reports   # ADD this import",
        "",
        "app.include_router(reports.router)   # ADD this line",
    ])

    pdf.label("Step 5 - Create Database Migration")
    pdf.code([
        "cd backend",
        "alembic revision --autogenerate -m 'Add reports table'",
        "alembic upgrade head",
    ])

    pdf.sub("Option C: Add a New Frontend Page")

    pdf.label("Step 6 - Create the Page Component")
    pdf.code([
        "# File: frontend/app/dashboard/reports/page.tsx",
        "'use client';",
        "import { useEffect, useState } from 'react';",
        "import { getReports } from '@/lib/api';",
        "",
        "export default function ReportsPage() {",
        "  const [reports, setReports] = useState([]);",
        "  useEffect(() => {",
        "    getReports().then(res => setReports(res.data));",
        "  }, []);",
        "  return (",
        "    <div className='p-8'>",
        "      <h1 className='text-2xl font-bold'>Reports</h1>",
        "      {reports.map(r => <div key={r.id}>{r.title}</div>)}",
        "    </div>",
        "  );",
        "}",
    ])

    pdf.label("Step 7 - Add API Helper to lib/api.ts")
    pdf.code([
        "# File: frontend/lib/api.ts",
        "export const getReports = () => api.get('/reports');",
        "export const createReport = (data: {title: string}) => api.post('/reports', data);",
    ])

    pdf.label("Step 8 - Add Navigation Link")
    pdf.code([
        "# File: frontend/app/dashboard/layout.tsx",
        "# Add to navItems array:",
        "{ href: '/dashboard/reports', label: 'Reports', icon: FileBarChart },",
    ])

    pdf.sub("Complete Checklist")
    pdf.table(
        ["Step", "File", "Action"],
        [
            ["1","backend/app/routers/reports.py","Create APIRouter with endpoints"],
            ["2","backend/app/schemas/reports.py","Create Pydantic input/output models"],
            ["3","backend/app/models/reports.py","Create SQLAlchemy DB model class"],
            ["4","backend/app/main.py","Import and register router"],
            ["5","Terminal (Alembic)","Generate and run migration"],
            ["6","frontend/app/dashboard/reports/page.tsx","Create React page component"],
            ["7","frontend/lib/api.ts","Add API helper functions"],
            ["8","frontend/app/dashboard/layout.tsx","Add nav link to sidebar"],
        ],
        [8, 72, 100]
    )


# ─────────────────────────────────────────────
# Section 9 - Starting Point
# ─────────────────────────────────────────────

def section9_starting_point(pdf):
    pdf.section("9", "Where Does Implementation Start?")

    pdf.sub("Backend Entry Point: backend/app/main.py")
    pdf.code([
        "# Start command:",
        "cd backend && uvicorn app.main:app --reload --port 8000",
        "",
        "# Startup sequence:",
        "1. Python loads backend/app/main.py",
        "2. FastAPI instance created: app = FastAPI(title='Requirements AI', version='1.0.0')",
        "3. Rate limiter attached: app.state.limiter = limiter",
        "4. Global exception handler registered (logs with UUID correlation ID)",
        "5. CORSMiddleware added (allows FRONTEND_URL origin, credentials)",
        "6. Nine routers registered:",
        "   app.include_router(auth.router)         # /auth",
        "   app.include_router(domain.router)        # /domains",
        "   app.include_router(upload.router)        # /input",
        "   app.include_router(requirements.router)  # /requirements",
        "   app.include_router(crosscheck.router)    # /crosscheck",
        "   app.include_router(srs.router)           # /srs",
        "   app.include_router(usecases.router)      # /usecases",
        "   app.include_router(admin.router)         # /admin",
        "   app.include_router(profile.router)       # /profile",
        "7. Uvicorn begins listening on port 8000",
        "8. API docs (Swagger UI): http://localhost:8000/docs",
    ])

    pdf.sub("Frontend Entry Point: frontend/app/page.tsx")
    pdf.code([
        "# Start command:",
        "cd frontend && npm run dev",
        "",
        "# Startup sequence:",
        "1. Next.js compiles TypeScript and starts on port 3000",
        "2. Browser navigates to http://localhost:3000",
        "3. Next.js loads app/layout.tsx (root layout: Geist fonts, metadata)",
        "4. Then loads app/page.tsx (root page):",
        "   - Checks localStorage for 'access_token'",
        "   - If found:     router.push('/dashboard')",
        "   - If not found: router.push('/auth')",
        "5. User lands on /auth (login / register)",
        "6. After successful login -> redirected to /dashboard/wizard",
    ])

    pdf.sub("First-Time Setup (Database)")
    pdf.code([
        "# 1. Create PostgreSQL database",
        "createdb reqTool",
        "",
        "# 2. Configure backend/.env",
        "DATABASE_URL=postgresql://postgres:password@localhost:5432/reqTool",
        "SECRET_KEY=your-random-secret-key-32-chars-min",
        "ANTHROPIC_API_KEY=sk-ant-...",
        "QDRANT_URL=http://localhost:6333",
        "FRONTEND_URL=http://localhost:3000",
        "",
        "# 3. Run all database migrations",
        "cd backend && alembic upgrade head",
        "",
        "# 4. Seed initial domains and questions",
        "cd backend && python -m app.seed",
        "",
        "# 5. Start Qdrant vector database (Docker)",
        "docker run -p 6333:6333 qdrant/qdrant",
    ])

    pdf.sub("Environment Variables (backend/.env)")
    pdf.table(
        ["Variable", "Purpose"],
        [
            ["DATABASE_URL","PostgreSQL connection: postgresql://user:pass@host:5432/db"],
            ["SECRET_KEY","JWT signing secret - keep private, at least 32 random characters"],
            ["ACCESS_TOKEN_EXPIRE_MINUTES","Access token lifetime (default: 15)"],
            ["REFRESH_TOKEN_EXPIRE_DAYS","Refresh token lifetime (default: 7)"],
            ["ANTHROPIC_API_KEY","Claude AI API key from console.anthropic.com"],
            ["QDRANT_URL","Qdrant vector DB URL (default: http://localhost:6333)"],
            ["FRONTEND_URL","CORS allowed origin (default: http://localhost:3000)"],
            ["SMTP_HOST / SMTP_PORT","Email server for password reset emails"],
            ["SMTP_USER / SMTP_PASSWORD","Email sender credentials"],
        ],
        [58, 122]
    )

    pdf.sub("Recommended Implementation Order (from scratch)")
    pdf.table(
        ["Phase", "Component", "Reason"],
        [
            ["1","Database models (models/)","Everything else depends on the data schema"],
            ["2","Alembic migrations","Creates the physical tables in PostgreSQL"],
            ["3","Core security (core/security.py)","Auth needed before any protected route works"],
            ["4","Auth routes (routers/auth.py)","Users must register/login first"],
            ["5","Domain & session routes","Foundation of the wizard flow"],
            ["6","AI integration (core/ai.py)","Core business logic of the system"],
            ["7","Requirements routes","Main product feature"],
            ["8","SRS, crosscheck, usecases","Value-add features built on top of requirements"],
            ["9","Admin routes","Management layer, added last"],
            ["10","Frontend (Next.js)","Build UI on top of a complete and tested API"],
        ],
        [10, 60, 110]
    )


# ─────────────────────────────────────────────
# Section 10 - Routes
# ─────────────────────────────────────────────

def section10_routes(pdf):
    pdf.section("10", "Complete API Route Reference")

    pdf.body(
        "All backend REST API endpoints. Base URL: http://localhost:8000  "
        "All authenticated routes require: Authorization: Bearer <access_token>"
    )

    groups = [
        ("Authentication (/auth)", [
            ("POST","/auth/register","Register new user account","No","-"),
            ("POST","/auth/login","Login - returns access + refresh tokens","No","-"),
            ("POST","/auth/logout","Revoke refresh token (logout)","Yes","-"),
            ("POST","/auth/refresh","Get new access token using refresh token","No","-"),
            ("GET", "/auth/me","Get current user profile","Yes","-"),
            ("POST","/auth/forgot-password","Request password reset email","No","-"),
            ("POST","/auth/reset-password","Reset password with emailed token","No","-"),
        ]),
        ("Domains & Sessions (/domains)", [
            ("GET", "/domains/","List domains filtered by country","Yes","-"),
            ("GET", "/domains/{domain_id}/questions","Get questions for a domain","Yes","-"),
            ("POST","/domains/session","Create user session with answers","Yes","-"),
        ]),
        ("Input Processing (/input)", [
            ("POST","/input/text","Process plain text with PII masking","Yes","-"),
            ("POST","/input/document","Upload PDF/DOCX for text extraction","Yes","-"),
        ]),
        ("Requirements (/requirements)", [
            ("POST","/requirements/generate","AI-generate requirements","Yes","10/min"),
            ("GET", "/requirements/{session_id}","Get all requirements for session","Yes","-"),
            ("GET", "/requirements/{session_id}/classified","Get classified FR/NFR","Yes","-"),
            ("PUT", "/requirements/{requirement_id}","Edit requirement (saves history)","Yes","-"),
        ]),
        ("Cross-Check (/crosscheck)", [
            ("GET","/crosscheck/{session_id}","Analyse requirements for conflicts","Yes","10/min"),
        ]),
        ("SRS Generation (/srs)", [
            ("POST","/srs/generate","Generate IEEE 830 SRS document","Yes","5/min"),
        ]),
        ("Use Cases (/usecases)", [
            ("POST","/usecases/generate","Generate use cases from requirements","Yes","10/min"),
        ]),
        ("Profile (/profile)", [
            ("GET","/profile/me","Get user profile","Yes","-"),
            ("PUT","/profile/update","Update name and email","Yes","-"),
            ("PUT","/profile/change-password","Change password (verifies current)","Yes","-"),
        ]),
        ("Admin (/admin) - Admin role required", [
            ("GET",   "/admin/stats","System statistics (users, sessions, reqs)","Admin","-"),
            ("GET",   "/admin/users","List all users with pagination","Admin","-"),
            ("PUT",   "/admin/users/{user_id}/toggle-active","Enable or disable user","Admin","-"),
            ("GET",   "/admin/sessions","List all user sessions","Admin","-"),
            ("GET",   "/admin/domains","List all domains","Admin","-"),
            ("POST",  "/admin/domains","Create new domain","Admin","-"),
            ("PUT",   "/admin/domains/{domain_id}","Update domain details","Admin","-"),
            ("DELETE","/admin/domains/{domain_id}","Soft-delete domain","Admin","-"),
            ("GET",   "/admin/domains/{domain_id}/questions","Get domain questions","Admin","-"),
            ("POST",  "/admin/domains/{domain_id}/questions","Add question to domain","Admin","-"),
            ("PUT",   "/admin/questions/{question_id}","Update a question","Admin","-"),
            ("DELETE","/admin/questions/{question_id}","Soft-delete a question","Admin","-"),
            ("GET",   "/admin/audit-log","Paginated audit log with filters","Admin","-"),
            ("GET",   "/admin/login-history","Login attempt history","Admin","-"),
            ("GET",   "/admin/login-history/failed-attempts","Failed logins last 24h","Admin","-"),
            ("GET",   "/admin/knowledge-base","List knowledge base PDFs","Admin","-"),
            ("POST",  "/admin/knowledge-base/upload","Upload PDF to knowledge base","Admin","-"),
            ("DELETE","/admin/knowledge-base/{entry_id}","Delete KB entry + embeddings","Admin","-"),
        ]),
    ]

    for group_name, routes in groups:
        pdf.sub(group_name)
        pdf.table(
            ["Method","Path","Purpose","Auth","Rate"],
            routes,
            [16, 68, 68, 14, 14]
        )

    pdf.sub("Frontend Routes (Next.js Pages)")
    pdf.table(
        ["URL Path", "Page File", "Access"],
        [
            ["/","app/page.tsx","Everyone (redirect only)"],
            ["/auth","app/auth/page.tsx","Unauthenticated only"],
            ["/auth/reset-password","app/auth/reset-password/page.tsx","Via reset email link"],
            ["/dashboard/wizard","app/dashboard/wizard/page.tsx","Authenticated users"],
            ["/dashboard/requirements","app/dashboard/requirements/page.tsx","Authenticated users"],
            ["/dashboard/profile","app/dashboard/profile/page.tsx","Authenticated users"],
            ["/dashboard/profile/change-password","app/dashboard/profile/change-password/page.tsx","Authenticated users"],
            ["/dashboard/admin","app/dashboard/admin/page.tsx","Admins only"],
            ["/dashboard/admin/users","app/dashboard/admin/users/page.tsx","Admins only"],
            ["/dashboard/admin/sessions","app/dashboard/admin/sessions/page.tsx","Admins only"],
            ["/dashboard/admin/domains","app/dashboard/admin/domains/page.tsx","Admins only"],
            ["/dashboard/admin/knowledge-base","app/dashboard/admin/knowledge-base/page.tsx","Admins only"],
            ["/dashboard/admin/audit-log","app/dashboard/admin/audit-log/page.tsx","Admins only"],
            ["/dashboard/admin/login-history","app/dashboard/admin/login-history/page.tsx","Admins only"],
        ],
        [62, 78, 40]
    )


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    pdf = DocPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(left=15, top=15, right=15)

    pdf.title_page()
    section1_overview(pdf)
    section2_stack(pdf)
    section3_auth(pdf)
    section4_architecture(pdf)
    section5_patterns(pdf)
    section6_database(pdf)
    section7_libraries(pdf)
    section8_add_domain(pdf)
    section9_starting_point(pdf)
    section10_routes(pdf)

    out = "project_documentation.pdf"
    pdf.output(out)
    print(f"PDF generated: {os.path.abspath(out)}")
    print(f"Total pages: {pdf.page}")


if __name__ == "__main__":
    main()
