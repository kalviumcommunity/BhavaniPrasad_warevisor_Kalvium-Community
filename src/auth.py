"""PostgreSQL authentication view (Login and Registration)."""

import streamlit as st
from src.db import authenticate_user, register_user
from src.theme import apply_theme


def render_auth_page():
    """Render PostgreSQL Login & Registration Portal without left sidebar panel."""
    apply_theme("auth")

    st.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #312e81 100%); border-radius: 16px; padding: 32px 36px; color: #ffffff; margin-bottom: 28px; box-shadow: 0 12px 30px -10px rgba(15, 23, 42, 0.3); text-align: center;">
        <div style="font-size: 2.2rem; font-weight: 800; letter-spacing: -0.5px; margin-bottom: 8px;">📦 RetailStock Manager & Supplier Portal</div>
        <div style="font-size: 1.05rem; color: #94a3b8;">Role-Based Inventory & Dispatch Management System</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2.2, 1])

    with col2:
        st.markdown('<div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 32px; box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.08);">', unsafe_allow_html=True)
        login_tab, signup_tab = st.tabs(["🔑 Log In", "📝 Register New Account"])

        with login_tab:
            st.subheader("Account Login")
            st.caption("Sign in using your registered PostgreSQL credentials.")
            
            with st.form("main_login_form"):
                ident = st.text_input("Username or Email Address", placeholder="e.g. manager@warevisor.com", key="auth_ident")
                pwd = st.text_input("Password", type="password", placeholder="Enter password", key="auth_pwd")
                submit_login = st.form_submit_button("Log In to Portal", use_container_width=True)

                if submit_login:
                    if not ident or not pwd:
                        st.warning("⚠️ Please enter both Username/Email and Password.")
                    else:
                        user = authenticate_user(ident, pwd)
                        if user:
                            st.session_state["authenticated"] = True
                            st.session_state["user_role"] = user["role"]
                            st.session_state["user_name"] = user["full_name"]
                            st.session_state["username"] = user["username"]
                            st.success(f"✅ Welcome back, **{user['full_name']}**!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials or account inactive. Please check your details.")

        with signup_tab:
            st.subheader("Create New PostgreSQL Account")
            st.caption("Registers a new user matching the PostgreSQL `app_users` table schema.")
            
            with st.form("main_signup_form"):
                reg_name = st.text_input("Full Name *", placeholder="e.g. Jane Doe", key="reg_name")
                reg_email = st.text_input("Email Address *", placeholder="e.g. jane@warevisor.com", key="reg_email")
                reg_uname = st.text_input("Username (Optional)", placeholder="Auto-generated if left blank", key="reg_uname")
                reg_role = st.selectbox("Account Role *", ["Manager (Central Admin)", "Product Sender (Supplier)"], key="reg_role")
                reg_pass = st.text_input("Password *", type="password", placeholder="Minimum 6 characters", key="reg_pass")
                reg_pass_conf = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password", key="reg_pass_conf")
                submit_signup = st.form_submit_button("Create Account & Register", use_container_width=True)

                if submit_signup:
                    if not reg_name or not reg_email or not reg_pass:
                        st.error("⚠️ Please fill in all required fields marked with *.")
                    elif reg_pass != reg_pass_conf:
                        st.error("❌ Passwords do not match.")
                    elif len(reg_pass) < 6:
                        st.warning("⚠️ Password must be at least 6 characters long.")
                    else:
                        role_str = "manager" if "Manager" in reg_role else "product_sender"
                        success, res = register_user(
                            full_name=reg_name,
                            email=reg_email,
                            password_hash=reg_pass,
                            role=role_str,
                            username=reg_uname
                        )
                        if success:
                            st.success(f"🎉 Account created for **{res['full_name']}** ({res['role']})!")
                            # Auto-login
                            st.session_state["authenticated"] = True
                            st.session_state["user_role"] = res["role"]
                            st.session_state["user_name"] = res["full_name"]
                            st.session_state["username"] = res["username"]
                            st.rerun()
                        else:
                            st.error(f"❌ Registration Failed: {res}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()
