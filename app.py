from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file
)

import sqlite3
import os
import io
import secrets

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import qrcode
from reportlab.pdfgen import canvas


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "portfolify-development-secret-change-before-production"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.path.join(BASE_DIR, "database.db")

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "uploads"
)

RESUME_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "resumes"
)

QR_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "qr_codes"
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESUME_FOLDER"] = RESUME_FOLDER
app.config["QR_FOLDER"] = QR_FOLDER

app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024


# =========================================================
# CREATE REQUIRED FOLDERS
# =========================================================

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESUME_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_IMAGE_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

ALLOWED_RESUME_EXTENSIONS = {
    "pdf"
}


# =========================================================
# PORTFOLIO OPTIONS
# =========================================================

ALLOWED_TEMPLATES = {
    "professional",
    "modern",
    "developer",
    "minimal",
    "creative",
    "dark"
}

ALLOWED_THEMES = {
    "blue",
    "purple",
    "green",
    "orange",
    "red",
    "dark"
}

ALLOWED_FONTS = {
    "modern",
    "classic",
    "clean",
    "typewriter"
}

ALLOWED_PHOTO_STYLES = {
    "circle",
    "rounded",
    "square"
}

ALLOWED_DECORATIONS = {
    "sparkle",
    "developer",
    "creative",
    "professional",
    "tech"
}


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# =========================================================
# DATABASE SETUP
# =========================================================

def init_db():

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            full_name TEXT,
            title TEXT,
            about TEXT,
            education TEXT,
            skills TEXT,
            projects TEXT,
            experience TEXT,

            github TEXT,
            linkedin TEXT,
            contact_email TEXT,

            username TEXT,

            published INTEGER DEFAULT 0,

            profile_photo TEXT,
            resume TEXT,

            template TEXT DEFAULT 'professional',
            theme TEXT DEFAULT 'purple',
            font TEXT DEFAULT 'modern',
            photo_style TEXT DEFAULT 'circle',
            decoration TEXT DEFAULT 'sparkle',

            FOREIGN KEY(user_id)
                REFERENCES users(id)
        )
    """)

    connection.commit()

    # Add missing columns to older databases
    add_column_if_missing(
        connection,
        "portfolios",
        "resume",
        "TEXT"
    )

    add_column_if_missing(
        connection,
        "portfolios",
        "theme",
        "TEXT DEFAULT 'purple'"
    )

    add_column_if_missing(
        connection,
        "portfolios",
        "font",
        "TEXT DEFAULT 'modern'"
    )

    add_column_if_missing(
        connection,
        "portfolios",
        "photo_style",
        "TEXT DEFAULT 'circle'"
    )

    add_column_if_missing(
        connection,
        "portfolios",
        "decoration",
        "TEXT DEFAULT 'sparkle'"
    )

    connection.commit()
    connection.close()


# =========================================================
# ADD DATABASE COLUMN IF MISSING
# =========================================================

def add_column_if_missing(
    connection,
    table_name,
    column_name,
    column_definition
):

    cursor = connection.cursor()

    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    columns = [
        row["name"]
        for row in cursor.fetchall()
    ]

    if column_name not in columns:

        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name}
            {column_definition}
            """
        )


# =========================================================
# LOGIN HELPERS
# =========================================================

def logged_in():

    return "user_id" in session


def current_user():

    if not logged_in():
        return None

    connection = get_db()

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    return user


# =========================================================
# FILE HELPERS
# =========================================================

def allowed_file(filename, allowed_extensions):

    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in allowed_extensions


def save_uploaded_file(
    uploaded_file,
    folder,
    allowed_extensions
):

    if not uploaded_file:
        return None

    if not uploaded_file.filename:
        return None

    if not allowed_file(
        uploaded_file.filename,
        allowed_extensions
    ):
        return None

    original_name = secure_filename(
        uploaded_file.filename
    )

    if not original_name:
        return None

    extension = original_name.rsplit(
        ".",
        1
    )[1].lower()

    random_name = (
        secrets.token_hex(12)
        + "."
        + extension
    )

    file_path = os.path.join(
        folder,
        random_name
    )

    uploaded_file.save(file_path)

    return random_name


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():

    return render_template(
        "index.html"
    )


# =========================================================
# SIGNUP
# =========================================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not name or not email or not password:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect(
                url_for("signup")
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("signup")
            )

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("signup")
            )

        connection = get_db()

        existing_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        if existing_user:

            connection.close()

            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        password_hash = generate_password_hash(
            password
        )

        connection.execute(
            """
            INSERT INTO users
            (
                name,
                email,
                password
            )
            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password_hash
            )
        )

        connection.commit()
        connection.close()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "signup.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_db()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if not user:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        password_valid = False

        try:

            password_valid = check_password_hash(
                user["password"],
                password
            )

        except Exception:

            password_valid = (
                user["password"] == password
            )

        if not password_valid:

            flash(
                "Invalid email or password.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        session["user_id"] = user["id"]

        flash(
            "Welcome back!",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("index")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    user = current_user()

    connection = get_db()

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    return render_template(
        "dashboard.html",
        user=user,
        portfolio=portfolio
    )


# =========================================================
# CREATE / EDIT PORTFOLIO
# =========================================================

@app.route(
    "/create",
    methods=["GET", "POST"]
)
def create():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db()

    existing_portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    if request.method == "POST":

        full_name = request.form.get(
            "name",
            ""
        ).strip()

        title = request.form.get(
            "title",
            ""
        ).strip()

        about = request.form.get(
            "about",
            ""
        ).strip()

        education = request.form.get(
            "education",
            ""
        ).strip()

        skills = request.form.get(
            "skills",
            ""
        ).strip()

        projects = request.form.get(
            "projects",
            ""
        ).strip()

        experience = request.form.get(
            "experience",
            ""
        ).strip()

        github = request.form.get(
            "github",
            ""
        ).strip()

        linkedin = request.form.get(
            "linkedin",
            ""
        ).strip()

        contact_email = request.form.get(
            "email",
            ""
        ).strip()

        template = request.form.get(
            "template",
            "professional"
        )

        theme = request.form.get(
            "theme",
            "purple"
        )

        font = request.form.get(
            "font",
            "modern"
        )

        photo_style = request.form.get(
            "photo_style",
            "circle"
        )

        decoration = request.form.get(
            "decoration",
            "sparkle"
        )

        if template not in ALLOWED_TEMPLATES:
            template = "professional"

        if theme not in ALLOWED_THEMES:
            theme = "purple"

        if font not in ALLOWED_FONTS:
            font = "modern"

        if photo_style not in ALLOWED_PHOTO_STYLES:
            photo_style = "circle"

        if decoration not in ALLOWED_DECORATIONS:
            decoration = "sparkle"

        photo = request.files.get("photo")

        resume = request.files.get("resume")

        photo_filename = None
        resume_filename = None

        if photo and photo.filename:

            photo_filename = save_uploaded_file(
                photo,
                UPLOAD_FOLDER,
                ALLOWED_IMAGE_EXTENSIONS
            )

            if not photo_filename:

                connection.close()

                flash(
                    "Invalid profile photo.",
                    "error"
                )

                return redirect(
                    url_for("create")
                )

        if resume and resume.filename:

            resume_filename = save_uploaded_file(
                resume,
                RESUME_FOLDER,
                ALLOWED_RESUME_EXTENSIONS
            )

            if not resume_filename:

                connection.close()

                flash(
                    "Only PDF resumes are allowed.",
                    "error"
                )

                return redirect(
                    url_for("create")
                )

        if existing_portfolio:

            if not photo_filename:

                photo_filename = existing_portfolio[
                    "profile_photo"
                ]

            if not resume_filename:

                resume_filename = existing_portfolio[
                    "resume"
                ]

            connection.execute(
                """
                UPDATE portfolios
                SET
                    full_name = ?,
                    title = ?,
                    about = ?,
                    education = ?,
                    skills = ?,
                    projects = ?,
                    experience = ?,
                    github = ?,
                    linkedin = ?,
                    contact_email = ?,
                    template = ?,
                    theme = ?,
                    font = ?,
                    photo_style = ?,
                    decoration = ?,
                    profile_photo = ?,
                    resume = ?
                WHERE id = ?
                """,
                (
                    full_name,
                    title,
                    about,
                    education,
                    skills,
                    projects,
                    experience,
                    github,
                    linkedin,
                    contact_email,
                    template,
                    theme,
                    font,
                    photo_style,
                    decoration,
                    photo_filename,
                    resume_filename,
                    existing_portfolio["id"]
                )
            )

        else:

            username = (
                full_name.lower()
                .replace(" ", "-")
            )

            connection.execute(
                """
                INSERT INTO portfolios
                (
                    user_id,
                    full_name,
                    title,
                    about,
                    education,
                    skills,
                    projects,
                    experience,
                    github,
                    linkedin,
                    contact_email,
                    username,
                    published,
                    profile_photo,
                    resume,
                    template,
                    theme,
                    font,
                    photo_style,
                    decoration
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    full_name,
                    title,
                    about,
                    education,
                    skills,
                    projects,
                    experience,
                    github,
                    linkedin,
                    contact_email,
                    username,
                    photo_filename,
                    resume_filename,
                    template,
                    theme,
                    font,
                    photo_style,
                    decoration
                )
            )

        connection.commit()
        connection.close()

        flash(
            "Portfolio saved successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard")
        )

    connection.close()

    return render_template(
        "create.html",
        portfolio=existing_portfolio
    )


# =========================================================
# PRIVATE PORTFOLIO PREVIEW
# =========================================================

@app.route("/portfolio")
def portfolio_preview():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db()

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    if not portfolio:

        flash(
            "Please create your portfolio first.",
            "warning"
        )

        return redirect(
            url_for("create")
        )

    return render_template(
        "portfolio.html",
        portfolio=portfolio,
        preview=True
    )


# =========================================================
# PUBLIC PORTFOLIO
# =========================================================

@app.route("/p/<int:portfolio_id>")
def public_portfolio(portfolio_id):

    connection = get_db()

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE id = ?
        AND published = 1
        """,
        (portfolio_id,)
    ).fetchone()

    connection.close()

    if not portfolio:

        return render_template(
            "404.html"
        ), 404

    return render_template(
        "portfolio.html",
        portfolio=portfolio,
        preview=False
    )


# =========================================================
# PUBLISH PORTFOLIO
# =========================================================

@app.route(
    "/portfolio/<int:portfolio_id>/publish",
    methods=["POST"]
)
def publish_portfolio(portfolio_id):

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db()

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE id = ?
        AND user_id = ?
        """,
        (
            portfolio_id,
            session["user_id"]
        )
    ).fetchone()

    if not portfolio:

        connection.close()

        flash(
            "Portfolio not found.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    connection.execute(
        """
        UPDATE portfolios
        SET published = 1
        WHERE id = ?
        """,
        (portfolio_id,)
    )

    connection.commit()
    connection.close()

    flash(
        "Your portfolio is now published.",
        "success"
    )

    return redirect(
        url_for("dashboard")
    )


# =========================================================
# UNPUBLISH PORTFOLIO
# =========================================================

@app.route(
    "/portfolio/<int:portfolio_id>/unpublish",
    methods=["POST"]
)
def unpublish_portfolio(portfolio_id):

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db()

    connection.execute(
        """
        UPDATE portfolios
        SET published = 0
        WHERE id = ?
        AND user_id = ?
        """,
        (
            portfolio_id,
            session["user_id"]
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Portfolio unpublished.",
        "success"
    )

    return redirect(
        url_for("dashboard")
    )


# =========================================================
# DELETE PORTFOLIO
# =========================================================

@app.route(
    "/portfolio/<int:portfolio_id>/delete",
    methods=["POST"]
)
def delete_portfolio(portfolio_id):

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db()

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE id = ?
        AND user_id = ?
        """,
        (
            portfolio_id,
            session["user_id"]
        )
    ).fetchone()

    if not portfolio:

        connection.close()

        flash(
            "Portfolio not found.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    connection.execute(
        """
        DELETE FROM portfolios
        WHERE id = ?
        AND user_id = ?
        """,
        (
            portfolio_id,
            session["user_id"]
        )
    )

    connection.commit()
    connection.close()

    flash(
        "Portfolio deleted.",
        "success"
    )

    return redirect(
        url_for("dashboard")
    )


# =========================================================
# ACCOUNT
# =========================================================

@app.route(
    "/account",
    methods=["GET", "POST"]
)
def account():

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db()

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        if not name or not email:

            connection.close()

            flash(
                "Name and email are required.",
                "error"
            )

            return redirect(
                url_for("account")
            )

        existing = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
            AND id != ?
            """,
            (
                email,
                session["user_id"]
            )
        ).fetchone()

        if existing:

            connection.close()

            flash(
                "This email is already in use.",
                "error"
            )

            return redirect(
                url_for("account")
            )

        connection.execute(
            """
            UPDATE users
            SET name = ?, email = ?
            WHERE id = ?
            """,
            (
                name,
                email,
                session["user_id"]
            )
        )

        connection.commit()

        flash(
            "Account updated successfully.",
            "success"
        )

    user = connection.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    return render_template(
        "account.html",
        user=user,
        portfolio=portfolio
    )


# =========================================================
# RESUME
# =========================================================

@app.route(
    "/resume/<int:portfolio_id>"
)
def resume(portfolio_id):

    connection = get_db()

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE id = ?
        AND published = 1
        """,
        (portfolio_id,)
    ).fetchone()

    connection.close()

    if not portfolio or not portfolio["resume"]:

        return "Resume not available.", 404

    file_path = os.path.join(
        RESUME_FOLDER,
        portfolio["resume"]
    )

    if not os.path.exists(file_path):

        return "Resume file not found.", 404

    return send_file(
        file_path,
        as_attachment=False
    )


# =========================================================
# QR CODE
# =========================================================

@app.route(
    "/qr/<int:portfolio_id>"
)
def qr_code(portfolio_id):

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db()

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE id = ?
        AND user_id = ?
        AND published = 1
        """,
        (
            portfolio_id,
            session["user_id"]
        )
    ).fetchone()

    connection.close()

    if not portfolio:

        return "Portfolio not found.", 404

    public_url = url_for(
        "public_portfolio",
        portfolio_id=portfolio_id,
        _external=True
    )

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(public_url)
    qr.make(fit=True)

    image = qr.make_image()

    image_bytes = io.BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    return send_file(
        image_bytes,
        mimetype="image/png",
        download_name="portfolio-qr.png"
    )


# =========================================================
# PDF
# =========================================================

@app.route(
    "/pdf/<int:portfolio_id>"
)
def portfolio_pdf(portfolio_id):

    if not logged_in():

        return redirect(
            url_for("login")
        )

    connection = get_db()

    portfolio = connection.execute(
        """
        SELECT *
        FROM portfolios
        WHERE id = ?
        AND user_id = ?
        """,
        (
            portfolio_id,
            session["user_id"]
        )
    ).fetchone()

    connection.close()

    if not portfolio:

        return "Portfolio not found.", 404

    pdf_buffer = io.BytesIO()

    pdf = canvas.Canvas(
        pdf_buffer
    )

    width, height = (
        595,
        842
    )

    y = height - 60

    pdf.setFont(
        "Helvetica-Bold",
        22
    )

    pdf.drawString(
        50,
        y,
        portfolio["full_name"] or "Portfolio"
    )

    y -= 30

    pdf.setFont(
        "Helvetica",
        13
    )

    pdf.drawString(
        50,
        y,
        portfolio["title"] or ""
    )

    y -= 35

    sections = [
        ("About", portfolio["about"]),
        ("Education", portfolio["education"]),
        ("Skills", portfolio["skills"]),
        ("Projects", portfolio["projects"]),
        ("Experience", portfolio["experience"])
    ]

    for heading, content in sections:

        if not content:
            continue

        pdf.setFont(
            "Helvetica-Bold",
            14
        )

        pdf.drawString(
            50,
            y,
            heading
        )

        y -= 20

        pdf.setFont(
            "Helvetica",
            10
        )

        lines = str(content).splitlines()

        for line in lines:

            if y < 50:

                pdf.showPage()

                y = height - 50

            safe_line = (
                line.encode(
                    "latin-1",
                    "replace"
                ).decode(
                    "latin-1"
                )
            )

            pdf.drawString(
                55,
                y,
                safe_line[:100]
            )

            y -= 15

        y -= 15

    pdf.save()

    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="portfolio.pdf"
    )


# =========================================================
# ERROR HANDLERS
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return (
        "<h1>404 - Page Not Found</h1>",
        404
    )


@app.errorhandler(413)
def file_too_large(error):

    return (
        "<h1>File Too Large</h1>"
        "<p>Maximum upload size is 8 MB.</p>",
        413
    )


# =========================================================
# START DATABASE
# =========================================================

init_db()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )