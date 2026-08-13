"""Authentication view (Login and Registration) styled with Dark Navy SaaS Enterprise UI."""

import textwrap
import streamlit as st
from src.db import authenticate_user, register_user
from src.theme import apply_theme


def render_auth_page():
    """Render SaaS Split-Screen Login & Registration Portal in Dark Navy theme."""
    apply_theme("auth")

    # Split-Screen Layout (Left: Dark Brand Hero Panel, Right: Dark Auth Form Card)
    left_col, right_col = st.columns([1.1, 1], gap="large")

    # ---------------------------------------------------------
    # LEFT PANEL: Dark Navy Brand Presentation & Analytics Visual
    # ---------------------------------------------------------
    with left_col:
        brand_html = (
            '<div style="background-color: #0B172A; border-radius: 18px; padding: 36px; color: #F8FAFC; border: 1px solid #1E293B; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);">'
            '<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">'
            '<div style="width: 42px; height: 42px; border-radius: 12px; background: linear-gradient(135deg, #2563eb, #1d4ed8); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 20px; color: white; box-shadow: 0 8px 16px rgba(37, 99, 235, 0.35);">📊</div>'
            '<div style="font-size: 22px; font-weight: 800; color: #F8FAFC;">WareVisor</div>'
            '</div>'
            '<h1 style="font-size: 28px; font-weight: 800; line-height: 1.25; color: #F8FAFC; margin: 0 0 12px 0;">Retail Data & Analytics Platform</h1>'
            '<p style="font-size: 14px; color: #94A3B8; line-height: 1.6; margin: 0 0 28px 0; font-weight: 400;">'
            'Manage retail records, explore performance trends, and turn your sales data into actionable business insights.'
            '</p>'
            '<div style="background-color: #101D31; border: 1px solid #1E293B; border-radius: 14px; padding: 20px;">'
            '<div style="font-size: 10px; font-weight: 800; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;">SYSTEM ANALYTICS OVERVIEW</div>'
            '<div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 12px;">'
            '<div>'
            '<div style="font-size: 11px; color: #64748B;">Total System Records</div>'
            '<div style="font-size: 24px; font-weight: 800; color: #F8FAFC;">307,477</div>'
            '</div>'
            '<div>'
            '<div style="font-size: 11px; color: #64748B; text-align: right;">Active Suppliers</div>'
            '<div style="font-size: 24px; font-weight: 800; color: #F8FAFC; text-align: right;">396</div>'
            '</div>'
            '</div>'
            '<svg viewBox="0 0 300 60" style="width: 100%; height: 50px; overflow: visible;">'
            '<path d="M0 45 Q 50 10, 100 35 T 200 15 T 300 25" fill="none" stroke="#38bdf8" stroke-width="3" stroke-linecap="round"/>'
            '<circle cx="100" cy="35" r="4" fill="#38bdf8" />'
            '<circle cx="200" cy="15" r="4" fill="#38bdf8" />'
            '<circle cx="300" cy="25" r="4" fill="#38bdf8" />'
            '</svg>'
            '</div>'
            '<div style="margin-top: 24px; padding-top: 18px; border-top: 1px solid #1E293B; font-size: 12px; color: #64748B; display: flex; gap: 16px;">'
            '<span>✓ High-Performance Analytics</span>'
            '<span>✓ Role-Based Access</span>'
            '</div>'
            '</div>'
        )
        st.markdown(brand_html, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # RIGHT PANEL: Dark Navy SaaS Login Form Card
    # ---------------------------------------------------------
    with right_col:
        header_html = (
            '<div style="margin-bottom: 16px;">'
            '<h2 style="font-size: 22px; font-weight: 800; color: #F8FAFC; margin: 0 0 4px 0;">Welcome back</h2>'
            '<p style="font-size: 13px; color: #94A3B8; margin: 0;">Sign in to your account to continue.</p>'
            '</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)

        login_tab, signup_tab = st.tabs(["🔑 Sign In", "📝 Register Account"])

        # LOGIN TAB
        with login_tab:
            with st.form("saas_login_form"):
                ident = st.text_input("Username or Email Address", placeholder="manager@warevisor.com", key="auth_ident")
                pwd = st.text_input("Password", type="password", placeholder="••••••••••••", key="auth_pwd")
                submit_login = st.form_submit_button("Sign In", use_container_width=True)

                if submit_login:
                    if not ident or not pwd:
                        st.markdown(
                            '<div style="background-color: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); color: #FCD34D; padding: 10px 14px; border-radius: 8px; font-size: 12px; margin-top: 12px; font-weight: 500;">'
                            '⚠️ Please enter both Username/Email and Password.'
                            '</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        user = authenticate_user(ident, pwd)
                        if user:
                            st.session_state["authenticated"] = True
                            st.session_state["user_role"] = user["role"]
                            st.session_state["user_name"] = user["full_name"]
                            st.session_state["username"] = user["username"]
                            st.rerun()
                        else:
                            st.markdown(
                                '<div style="background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #FCA5A5; padding: 10px 14px; border-radius: 8px; font-size: 12px; margin-top: 12px; font-weight: 500;">'
                                'Invalid username or password'
                                '</div>',
                                unsafe_allow_html=True
                            )

        # REGISTER TAB
        with signup_tab:
            with st.form("saas_signup_form"):
                reg_name = st.text_input("Full Name *", placeholder="Jane Doe", key="reg_name")
                reg_email = st.text_input("Email Address *", placeholder="jane@warevisor.com", key="reg_email")
                reg_uname = st.text_input("Username (Optional)", placeholder="Auto-generated if left blank", key="reg_uname")
                reg_role = st.selectbox("Account Role *", ["Manager", "Product Sender"], key="reg_role")
                reg_pass = st.text_input("Password *", type="password", placeholder="Minimum 6 characters", key="reg_pass")
                reg_pass_conf = st.text_input("Confirm Password *", type="password", placeholder="Re-enter password", key="reg_pass_conf")
                submit_signup = st.form_submit_button("Create Account", use_container_width=True)

                if submit_signup:
                    if not reg_name or not reg_email or not reg_pass:
                        st.markdown(
                            '<div style="background-color: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); color: #FCD34D; padding: 10px 14px; border-radius: 8px; font-size: 12px; margin-top: 12px;">'
                            '⚠️ Please fill in all required fields marked with *.'
                            '</div>',
                            unsafe_allow_html=True
                        )
                    elif reg_pass != reg_pass_conf:
                        st.markdown(
                            '<div style="background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #FCA5A5; padding: 10px 14px; border-radius: 8px; font-size: 12px; margin-top: 12px;">'
                            '❌ Passwords do not match.'
                            '</div>',
                            unsafe_allow_html=True
                        )
                    elif len(reg_pass) < 6:
                        st.markdown(
                            '<div style="background-color: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.3); color: #FCD34D; padding: 10px 14px; border-radius: 8px; font-size: 12px; margin-top: 12px;">'
                            '⚠️ Password must be at least 6 characters long.'
                            '</div>',
                            unsafe_allow_html=True
                        )
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
                            st.session_state["authenticated"] = True
                            st.session_state["user_role"] = res["role"]
                            st.session_state["user_name"] = res["full_name"]
                            st.session_state["username"] = res["username"]
                            st.rerun()
                        else:
                            st.markdown(
                                '<div style="background-color: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #FCA5A5; padding: 10px 14px; border-radius: 8px; font-size: 12px; margin-top: 12px;">'
                                f'Registration Failed: {res}'
                                '</div>',
                                unsafe_allow_html=True
                            )
