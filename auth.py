
import base64
import sqlite3
from pathlib import Path

import bcrypt
import streamlit as st


DB_NAME = "geneweaver_users.db"
BACKGROUND_IMAGE = Path(__file__).with_name("login_bg.png")


# ==================================================
# DATABASE FUNCTIONS
# ==================================================

def initialize_database():
    conn = sqlite3.connect(DB_NAME)

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                username TEXT NOT NULL,
                password_hash BLOB NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()


def register_user(full_name, email, username, password):

    if not all([full_name, email, username, password]):
        return False, "Please fill in all fields."

    if len(password.encode("utf-8")) > 72:
        return False, "Password must be 72 bytes or fewer."

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE username=? OR email=?",
            (username, email)
        )

        if cursor.fetchone():
            return False, "Username or email already exists."

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        cursor.execute("""
            INSERT INTO users
            (full_name, email, username, password_hash)
            VALUES (?, ?, ?, ?)
        """, (
            full_name,
            email,
            username,
            password_hash
        ))

        conn.commit()

        return True, "Account created successfully! Please log in."

    finally:
        conn.close()


def login_user(username_or_email, password):

    conn = sqlite3.connect(DB_NAME)

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT full_name, password_hash
            FROM users
            WHERE username=? OR email=?
        """, (
            username_or_email,
            username_or_email
        ))

        user = cursor.fetchone()

    finally:
        conn.close()

    if user and bcrypt.checkpw(
        password.encode("utf-8"),
        user[1]
    ):
        return True, user[0]

    return False, None


# ==================================================
# BACKGROUND IMAGE
# ==================================================

def get_background_image():

    if not BACKGROUND_IMAGE.exists():
        return None

    image_bytes = BACKGROUND_IMAGE.read_bytes()

    encoded = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    return f"data:image/png;base64,{encoded}"


# ==================================================
# LOGIN PAGE DESIGN
# ==================================================

def apply_login_css(background):

    if background:
        background_style = f"""
            background-image: url("{background}");
            background-position: center center;
            background-repeat: no-repeat;
            background-size: 100% 100%;
        """
    else:
        background_style = """
            background:
                linear-gradient(135deg, #020817, #071b3d);
        """

    st.markdown(f"""
    <style>

    /* FULL SCREEN BACKGROUND */

    [data-testid="stAppViewContainer"] {{
        {background_style}
        min-height: 100vh;
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    footer,
    #MainMenu {{
        display: none !important;
    }}

    [data-testid="stMain"] {{
        background: transparent !important;
    }}

    .block-container {{
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }}


    /* LOGIN PANEL POSITION */

    .st-key-geneweaver_auth_overlay {{
        position: fixed !important;
        z-index: 9999 !important;

        top: 41.2vh !important;
        left: 62.15vw !important;

        width: 29.15vw !important;
        max-width: 490px !important;
        min-width: 300px !important;

        padding: 0 !important;
        margin: 0 !important;

        background: transparent !important;
    }}


    /* LOGIN AND REGISTER TABS */

    .st-key-geneweaver_auth_overlay
    [data-baseweb="tab-list"] {{
        gap: 4px !important;
        border-bottom: 0 !important;
        background: transparent !important;
    }}

    .st-key-geneweaver_auth_overlay
    button[data-baseweb="tab"] {{
        color: white !important;

        background: rgba(3, 24, 62, 0.85) !important;

        border: 1px solid #159eea !important;
        border-radius: 13px 13px 0 0 !important;

        padding: 9px 8px !important;
        min-height: 42px !important;

        flex: 1 !important;
    }}

    .st-key-geneweaver_auth_overlay
    button[data-baseweb="tab"][aria-selected="true"] {{
        color: white !important;

        background: linear-gradient(
            105deg,
            #00bfff,
            #174fff
        ) !important;

        box-shadow: 0 0 16px #00d2ff !important;
        border-color: #28dcff !important;
    }}

    .st-key-geneweaver_auth_overlay
    [data-testid="stTabContent"] {{
        padding: 12px 2px 0 !important;
        background: transparent !important;
    }}


    /* INPUT FIELDS */

    .st-key-geneweaver_auth_overlay label,
    .st-key-geneweaver_auth_overlay p {{
        color: #eaf6ff !important;
    }}

    .st-key-geneweaver_auth_overlay input {{
        color: white !important;

        background: rgba(8, 29, 67, 0.96) !important;

        border: 1px solid #4d9fe8 !important;
        border-radius: 15px !important;

        min-height: 43px !important;

        box-shadow: inset 0 0 12px
            rgba(0, 110, 255, 0.12) !important;
    }}

    .st-key-geneweaver_auth_overlay input::placeholder {{
        color: #a9c3e5 !important;
    }}

    .st-key-geneweaver_auth_overlay input:focus {{
        border-color: #00eaff !important;
        box-shadow: 0 0 12px #00eaff70 !important;
    }}


    /* REMEMBER ME */

    .st-key-geneweaver_auth_overlay
    [data-testid="stCheckbox"] {{
        margin: 2px 0 7px !important;
    }}


    /* LOGIN BUTTON */

    .st-key-geneweaver_auth_overlay
    [data-testid="stFormSubmitButton"] button {{

        width: 100% !important;
        min-height: 48px !important;

        color: white !important;
        font-size: 17px !important;
        font-weight: 800 !important;

        border: 1px solid #39eaff !important;
        border-radius: 28px !important;

        background: linear-gradient(
            100deg,
            #00cfff,
            #145dff 58%,
            #a33cff
        ) !important;

        box-shadow: 0 0 18px #00aeff !important;

    }}

    .st-key-geneweaver_auth_overlay
    [data-testid="stFormSubmitButton"] button:hover {{
        filter: brightness(1.15);
        box-shadow: 0 0 25px #00e1ff !important;
    }}


    /* ERROR AND SUCCESS MESSAGES */

    .st-key-geneweaver_auth_overlay
    [data-testid="stAlert"] {{
        background: rgba(4, 19, 48, 0.96) !important;
        border: 1px solid #258ed4 !important;
    }}


    /* MOBILE RESPONSIVE DESIGN */

    @media (max-width: 850px) {{

        [data-testid="stAppViewContainer"] {{
            background-size: cover !important;
            background-position: 40% center !important;
        }}

        .st-key-geneweaver_auth_overlay {{
            top: 24vh !important;
            left: 5vw !important;

            width: 90vw !important;
            max-width: none !important;
            min-width: 0 !important;

            padding: 18px !important;

            border: 1px solid #28cfff !important;
            border-radius: 20px !important;

            background: rgba(3, 18, 48, 0.94) !important;

            box-shadow: 0 0 25px #007bff75 !important;
        }}
    }}

    </style>
    """, unsafe_allow_html=True)


# ==================================================
# MAIN LOGIN FUNCTION
# ==================================================

def require_login():

    initialize_database()

    if st.session_state.get("logged_in", False):
        return True

    background = get_background_image()

    apply_login_css(background)

    if background is None:
        st.warning(
            "login_bg.png not found. "
            "Place the reference image beside auth.py."
        )

    with st.container(key="geneweaver_auth_overlay"):

        login_tab, register_tab = st.tabs([
            "🔐 Login",
            "👤 Create Account"
        ])

        # ---------------- LOGIN ----------------

        with login_tab:

            with st.form("geneweaver_login_form"):

                username = st.text_input(
                    "Username or Email",
                    placeholder="Username or Email"
                )

                password = st.text_input(
                    "Password",
                    placeholder="Password",
                    type="password"
                )

                st.checkbox(
                    "Remember Me",
                    key="remember_login"
                )

                submitted = st.form_submit_button(
                    "Login  ➜",
                    use_container_width=True
                )

                if submitted:

                    if not username.strip() or not password:
                        st.error(
                            "Please enter your username/email and password."
                        )

                    else:

                        success, full_name = login_user(
                            username.strip(),
                            password
                        )

                        if success:

                            st.session_state.logged_in = True

                            st.session_state.full_name = full_name

                            st.rerun()

                        else:

                            st.error(
                                "Incorrect username/email or password."
                            )


        # ---------------- REGISTER ----------------

        with register_tab:

            with st.form("geneweaver_register_form"):

                full_name = st.text_input(
                    "Full Name",
                    placeholder="Full Name"
                )

                email = st.text_input(
                    "Email Address",
                    placeholder="Email Address"
                )

                new_username = st.text_input(
                    "Username",
                    placeholder="Choose a username"
                )

                new_password = st.text_input(
                    "Password",
                    placeholder="Create a password",
                    type="password"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    placeholder="Confirm your password",
                    type="password"
                )

                submitted = st.form_submit_button(
                    "Create Account ➜",
                    use_container_width=True
                )

                if submitted:

                    if new_password != confirm_password:

                        st.error("Passwords do not match.")

                    else:

                        success, message = register_user(
                            full_name.strip(),
                            email.strip(),
                            new_username.strip(),
                            new_password
                        )

                        if success:
                            st.success(message)

                        else:
                            st.error(message)

    st.stop()


# ==================================================
# LOGOUT FUNCTION
# ==================================================

def logout_user():

    st.session_state.logged_in = False

    st.session_state.pop("full_name", None)

    st.session_state.pop("remember_login", None)

    st.rerun()
