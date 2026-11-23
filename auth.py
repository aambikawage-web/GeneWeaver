
import streamlit as st
import sqlite3
import bcrypt
import re

DB_NAME = "geneweaver_users.db"


# --------------------------------------------------
# DATABASE INITIALIZATION
# --------------------------------------------------

def initialize_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL COLLATE NOCASE UNIQUE,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash BLOB NOT NULL
            )
        """)


# --------------------------------------------------
# USER REGISTRATION
# --------------------------------------------------

def register_user(full_name, email, username, password):

    full_name = full_name.strip()
    email = email.strip().lower()
    username = username.strip()

    if not all([full_name, email, username, password]):
        return False, "Please fill in all fields."

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return False, "Please enter a valid email address."

    if len(username) < 3:
        return False, "Username must have at least 3 characters."

    if len(password) < 8:
        return False, "Password must have at least 8 characters."

    if len(password.encode("utf-8")) > 72:
        return False, "Password must be at most 72 bytes."

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("""
                INSERT INTO users
                (full_name, email, username, password_hash)
                VALUES (?, ?, ?, ?)
            """, (
                full_name,
                email,
                username,
                password_hash
            ))

        return True, "Account created successfully!"

    except sqlite3.IntegrityError:
        return False, "Email or username is already registered."


# --------------------------------------------------
# USER LOGIN
# --------------------------------------------------

def login_user(identifier, password):

    identifier = identifier.strip()

    with sqlite3.connect(DB_NAME) as conn:
        user = conn.execute("""
            SELECT full_name, username, password_hash
            FROM users
            WHERE username = ? OR email = ?
        """, (
            identifier,
            identifier
        )).fetchone()

    if user is None:
        return False, None

    try:
        valid = bcrypt.checkpw(
            password.encode("utf-8"),
            user[2]
        )
    except (ValueError, TypeError):
        valid = False

    if valid:
        return True, {
            "full_name": user[0],
            "username": user[1]
        }

    return False, None


# --------------------------------------------------
# LOGIN PAGE DESIGN
# --------------------------------------------------

def login_page_css():

    st.markdown("""
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at 10% 15%,
                #172554 0%,
                transparent 35%
            ),
            radial-gradient(
                circle at 90% 85%,
                #312e81 0%,
                transparent 35%
            ),
            #070d1c;
    }

    .main .block-container {
        max-width: 1200px;
        padding-top: 3rem;
    }

    .login-title {
        text-align: center;
        font-size: 52px;
        font-weight: 900;
        background: linear-gradient(
            90deg,
            #22d3ee,
            #818cf8,
            #c084fc
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
    }

    .login-subtitle {
        text-align: center;
        color: #a5b4fc;
        font-size: 15px;
        letter-spacing: 2px;
        margin-bottom: 30px;
    }

    div[data-testid="stForm"] {
        background: rgba(20, 32, 57, 0.88);
        border: 1px solid #334e75;
        border-radius: 18px;
        padding: 25px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.35);
    }

    .stTextInput input {
        background: #101d33 !important;
        color: white !important;
        border: 1px solid #405579 !important;
        border-radius: 9px !important;
    }

    .stFormSubmitButton button {
        background: linear-gradient(
            90deg,
            #0891b2,
            #6366f1
        ) !important;
        color: white !important;
        border: none !important;
        border-radius: 9px !important;
        height: 45px;
        font-weight: 700;
    }

    .stTabs [data-baseweb="tab"] {
        color: #cbd5e1;
        font-weight: 600;
    }

    </style>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# LOGIN AND REGISTRATION INTERFACE
# --------------------------------------------------

def require_login():

    initialize_database()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return True

    login_page_css()

    st.markdown(
        '<div class="login-title">🧬 GeneWeaver</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="login-subtitle">'
        'NEXT-GENERATION DNA SEQUENCE ANALYSIS PLATFORM'
        '</div>',
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1, 1.5, 1])

    with center:

        login_tab, register_tab = st.tabs([
            "🔐 Login",
            "✨ Create Account"
        ])

        # LOGIN TAB

        with login_tab:

            st.markdown("### Welcome Back")

            st.caption(
                "Sign in to access your DNA analysis workspace."
            )

            with st.form("login_form"):

                identifier = st.text_input(
                    "Username or Email",
                    placeholder="Enter your username or email"
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password"
                )

                login_button = st.form_submit_button(
                    "Sign In →",
                    use_container_width=True
                )

            if login_button:

                if not identifier.strip() or not password:
                    st.error("Please enter your login details.")

                else:

                    success, user = login_user(
                        identifier,
                        password
                    )

                    if success:

                        st.session_state.logged_in = True
                        st.session_state.full_name = user["full_name"]
                        st.session_state.username = user["username"]

                        st.rerun()

                    else:
                        st.error(
                            "Invalid username/email or password. "
                            "Please register first if you are a new user."
                        )

        # REGISTRATION TAB

        with register_tab:

            st.markdown("### Join GeneWeaver")

            st.caption(
                "Create your account to start exploring DNA sequences."
            )

            with st.form("register_form"):

                full_name = st.text_input(
                    "Full Name",
                    placeholder="Enter your full name"
                )

                email = st.text_input(
                    "Email Address",
                    placeholder="Enter your email"
                )

                username = st.text_input(
                    "Username",
                    placeholder="Choose a username"
                )

                new_password = st.text_input(
                    "Create Password",
                    type="password",
                    placeholder="Minimum 8 characters"
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Re-enter your password"
                )

                register_button = st.form_submit_button(
                    "Create My Account →",
                    use_container_width=True
                )

            if register_button:

                if new_password != confirm_password:
                    st.error("Passwords do not match.")

                else:

                    success, message = register_user(
                        full_name,
                        email,
                        username,
                        new_password
                    )

                    if success:
                        st.success(
                            message + " Please go to Login."
                        )

                    else:
                        st.error(message)

    st.markdown(
        "<p style='text-align:center;color:#64748b;"
        "font-size:12px;margin-top:35px;'>"
        "GENEWEAVER • DNA ALIGNMENT • BIOINFORMATICS"
        "</p>",
        unsafe_allow_html=True
    )

    return False
