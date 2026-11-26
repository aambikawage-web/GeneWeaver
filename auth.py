
import sqlite3
from pathlib import Path

import bcrypt
import streamlit as st


# ==================================================
# DATABASE CONFIGURATION
# ==================================================

DB_NAME = Path(__file__).with_name("geneweaver_users.db")


# ==================================================
# DATABASE FUNCTIONS
# ==================================================

def initialize_database():
    conn = sqlite3.connect(str(DB_NAME))

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

    full_name = full_name.strip()
    email = email.strip().lower()
    username = username.strip()

    if not all([full_name, email, username, password]):
        return False, "Please fill in all fields."

    if "@" not in email or "." not in email:
        return False, "Please enter a valid email address."

    if len(password.encode("utf-8")) > 72:
        return False, "Password must be 72 bytes or fewer."

    conn = sqlite3.connect(str(DB_NAME))

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM users
            WHERE LOWER(username) = LOWER(?)
               OR LOWER(email) = LOWER(?)
        """, (username, email))

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

    except sqlite3.Error as error:
        return False, f"Database error: {error}"

    finally:
        conn.close()


def login_user(username_or_email, password):

    if not username_or_email or not password:
        return False, None

    conn = sqlite3.connect(str(DB_NAME))

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT full_name, password_hash
            FROM users
            WHERE LOWER(username) = LOWER(?)
               OR LOWER(email) = LOWER(?)
        """, (
            username_or_email.strip(),
            username_or_email.strip()
        ))

        user = cursor.fetchone()

    except sqlite3.Error:
        user = None

    finally:
        conn.close()

    if user:
        try:
            stored_hash = user[1]

            if isinstance(stored_hash, memoryview):
                stored_hash = stored_hash.tobytes()

            if bcrypt.checkpw(
                password.encode("utf-8"),
                bytes(stored_hash)
            ):
                return True, user[0]

        except (ValueError, TypeError):
            pass

    return False, None


# ==================================================
# LOGIN PAGE CSS
# ==================================================

def apply_login_css():

    st.markdown("""
    <style>

    /* MAIN PAGE */

    .stApp {
        background:
            radial-gradient(
                circle at 0% 25%,
                rgba(0, 210, 210, 0.16),
                transparent 42%
            ),
            radial-gradient(
                circle at 100% 20%,
                rgba(20, 65, 180, 0.20),
                transparent 45%
            ),
            linear-gradient(
                120deg,
                #031b2c,
                #03132b 55%,
                #04183d
            );

        color: #f8fafc;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    footer,
    #MainMenu {
        display: none !important;
    }

    [data-testid="stMain"] {
        background: transparent !important;
    }

    .block-container {
        max-width: 1500px !important;
        padding: 3.5rem 4rem 2rem 4rem !important;
    }


    /* LEFT HERO SECTION */

    .hero-logo {
        color: #08d9f5;
        font-size: 29px;
        font-weight: 850;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }

    .hero-subtitle {
        color: #a5d8f7;
        font-size: 12px;
        letter-spacing: 4px;
        font-weight: 600;
        margin-bottom: 75px;
    }

    .hero-title {
        color: #ffffff;
        font-size: clamp(38px, 4vw, 62px);
        line-height: 1.18;
        font-weight: 900;
        margin-bottom: 25px;
    }

    .hero-title span {
        color: #05d7f5;
    }

    .hero-description {
        color: #d5e8fa;
        font-size: 17px;
        line-height: 1.9;
        margin-bottom: 36px;
    }

    .feature {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 22px 0;
        color: #ffffff;
        font-size: 15px;
        line-height: 1.7;
    }

    .feature-icon {
        min-width: 47px;
        height: 47px;
        border: 1px solid #078eb8;
        border-radius: 13px;
        background: rgba(0, 180, 220, 0.12);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 23px;
    }

    .feature strong {
        color: #ffffff;
        font-size: 15px;
    }


    /* RIGHT LOGIN CARD */

    .st-key-geneweaver_auth_card {
        background: rgba(4, 25, 59, 0.88) !important;
        border: 1px solid #00c9f5 !important;
        border-radius: 27px !important;
        padding: 28px 28px 25px 28px !important;
        box-shadow:
            0 0 30px rgba(0, 174, 255, 0.16),
            inset 0 0 25px rgba(0, 100, 200, 0.06) !important;
    }

    .auth-heading {
        text-align: center;
        color: #04d9f5;
        font-size: 33px;
        font-weight: 850;
        margin-bottom: 5px;
    }

    .auth-subheading {
        text-align: center;
        color: #c4ddf8;
        font-size: 15px;
        margin-bottom: 25px;
    }


    /* TABS */

    .st-key-geneweaver_auth_card [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid rgba(90, 140, 200, 0.15);
    }

    .st-key-geneweaver_auth_card button[data-baseweb="tab"] {
        color: #b9cce6 !important;
        font-weight: 650 !important;
    }

    .st-key-geneweaver_auth_card
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ff5868 !important;
        border-bottom-color: #ff5868 !important;
    }

    .st-key-geneweaver_auth_card [data-testid="stTabContent"] {
        padding-top: 18px;
    }


    /* LABELS AND INPUTS */

    .st-key-geneweaver_auth_card label {
        color: #edf6ff !important;
        font-weight: 600 !important;
    }

    .st-key-geneweaver_auth_card input {
        background: #142b4e !important;
        color: #ffffff !important;
        border: 1px solid #8bbce8 !important;
        border-radius: 11px !important;
        min-height: 43px !important;
    }

    .st-key-geneweaver_auth_card input::placeholder {
        color: #a9c3e2 !important;
    }

    .st-key-geneweaver_auth_card input:focus {
        border-color: #00dcff !important;
        box-shadow: 0 0 12px rgba(0, 220, 255, 0.3) !important;
    }

    .st-key-geneweaver_auth_card
    [data-testid="stCheckbox"] label {
        color: #e5f1ff !important;
    }


    /* LOGIN AND REGISTER BUTTONS */

    .st-key-geneweaver_auth_card
    [data-testid="stFormSubmitButton"] button {

        width: 100% !important;
        min-height: 49px !important;

        color: white !important;
        font-size: 16px !important;
        font-weight: 750 !important;

        border: 1px solid #35e5ff !important;
        border-radius: 30px !important;

        background: linear-gradient(
            100deg,
            #00c9ef,
            #1765ff 58%,
            #a02cff
        ) !important;

        box-shadow: 0 0 19px rgba(0, 190, 255, 0.5) !important;

        transition: 0.2s ease;
    }

    .st-key-geneweaver_auth_card
    [data-testid="stFormSubmitButton"] button:hover {
        filter: brightness(1.15);
        box-shadow: 0 0 27px rgba(0, 210, 255, 0.7) !important;
    }


    /* ALERTS */

    .st-key-geneweaver_auth_card [data-testid="stAlert"] {
        background: rgba(5, 30, 65, 0.95) !important;
        border-radius: 10px !important;
    }


    /* MOBILE */

    @media (max-width: 850px) {

        .block-container {
            padding: 1.5rem 1rem !important;
        }

        .hero-subtitle {
            margin-bottom: 25px;
        }

        .hero-title {
            font-size: 38px;
        }

        .hero-description {
            font-size: 15px;
        }

        .st-key-geneweaver_auth_card {
            padding: 20px !important;
            margin-top: 20px;
        }
    }

    </style>
    """, unsafe_allow_html=True)


# ==================================================
# LOGIN PAGE
# ==================================================

def require_login():

    initialize_database()

    if st.session_state.get("logged_in", False):
        return True

    apply_login_css()

    # Two-column login page
    left_column, right_column = st.columns(
        [1.08, 1],
        gap="large",
        vertical_alignment="center"
    )

    # ----------------------------------------------
    # LEFT SIDE: GENEWEAVER INTRODUCTION
    # ----------------------------------------------

    with left_column:

        st.markdown("""
        <div class="hero-logo">
            🧬 GeneWeaver
        </div>

        <div class="hero-subtitle">
            GPU-ACCELERATED CRISPR ALIGNMENT ENGINE
        </div>

        <div class="hero-title">
            Unlock the<br>
            <span>Secrets</span> of DNA
        </div>

        <div class="hero-description">
            Explore, analyze and compare DNA sequences with an
            intelligent alignment workspace.<br>
            Discover patterns and understand genetic data
            through powerful alignment tools.
        </div>

        <div class="feature">
            <div class="feature-icon">🧬</div>
            <div>
                <strong>DNA Sequence Alignment</strong><br>
                Needleman-Wunsch and Smith-Waterman
            </div>
        </div>

        <div class="feature">
            <div class="feature-icon">📊</div>
            <div>
                <strong>DNA Statistics &amp; Visualizations</strong><br>
                GC content and nucleotide analysis
            </div>
        </div>

        <div class="feature">
            <div class="feature-icon">⚡</div>
            <div>
                <strong>GPU-Accelerated Processing</strong><br>
                CPU and GPU alignment comparison
            </div>
        </div>

        <div class="feature">
            <div class="feature-icon">🔬</div>
            <div>
                <strong>Research Workspace</strong><br>
                Upload FASTA files and analyze sequences
            </div>
        </div>
        """, unsafe_allow_html=True)


    # ----------------------------------------------
    # RIGHT SIDE: LOGIN CARD
    # ----------------------------------------------

    with right_column:

        with st.container(key="geneweaver_auth_card"):

            st.markdown("""
            <div class="auth-heading">
                🧬 GeneWeaver
            </div>

            <div class="auth-subheading">
                Secure Research Workspace
            </div>
            """, unsafe_allow_html=True)

            login_tab, register_tab = st.tabs([
                "🔐 Login",
                "👤 Create Account"
            ])

            # --------------------------------------
            # LOGIN
            # --------------------------------------

            with login_tab:

                with st.form("geneweaver_login_form"):

                    username_or_email = st.text_input(
                        "Username or Email",
                        placeholder="Enter username or email"
                    )

                    password = st.text_input(
                        "Password",
                        placeholder="Enter your password",
                        type="password"
                    )

                    st.checkbox(
                        "Remember Me",
                        key="remember_login"
                    )

                    submitted = st.form_submit_button(
                        "Login ➜",
                        use_container_width=True
                    )

                    if submitted:

                        if not username_or_email.strip() or not password:
                            st.error(
                                "Please enter your username/email and password."
                            )

                        else:

                            success, full_name = login_user(
                                username_or_email,
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


            # --------------------------------------
            # CREATE ACCOUNT
            # --------------------------------------

            with register_tab:

                with st.form("geneweaver_register_form"):

                    full_name = st.text_input(
                        "Full Name",
                        placeholder="Enter your full name"
                    )

                    email = st.text_input(
                        "Email Address",
                        placeholder="Enter your email address"
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
                                full_name,
                                email,
                                new_username,
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
    st.session_state.pop("username", None)
    st.session_state.pop("remember_login", None)

    st.session_state.alignment_result = None
    st.session_state.chat_messages = []

    st.rerun()
