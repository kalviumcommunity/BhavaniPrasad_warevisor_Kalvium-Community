"""WareVisor Enterprise Application Entry Point.

Can be run directly via `python app.py` or via `streamlit run app.py`.
"""

import sys
import subprocess
import streamlit as st

def main():
    """Main Streamlit Application Layout & Router."""
    from src.db import init_db
    from src.auth import render_auth_page
    from src.manager import render_manager_portal
    from src.sender import render_sender_portal

    # Initialize Session State
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "user_role" not in st.session_state:
        st.session_state["user_role"] = None
    if "user_name" not in st.session_state:
        st.session_state["user_name"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None

    # Ensure PostgreSQL database is initialized
    init_db()

    # Application Flow: Login -> Dashboard
    if not st.session_state["authenticated"]:
        render_auth_page()
    else:
        if st.session_state["user_role"] == "manager":
            render_manager_portal()
        else:
            render_sender_portal()


if __name__ == "__main__":
    # Check if executed inside Streamlit runtime
    try:
        from streamlit.runtime import exists
        running_in_streamlit = exists()
    except Exception:
        running_in_streamlit = False

    if running_in_streamlit:
        main()
    else:
        # If executed via `python app.py`, automatically launch Streamlit
        print("==================================================")
        print("WareVisor RetailStock Manager Application Starting!")
        print("Launching Streamlit app.py...")
        print("==================================================")
        cmd = [sys.executable, "-m", "streamlit", "run", __file__]
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            print("\nServer stopped gracefully.")
