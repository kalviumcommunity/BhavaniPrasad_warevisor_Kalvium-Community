import os
import sys
import subprocess

os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"
os.environ["ARROW_DEFAULT_MEMORY_POOL"] = "system"
os.environ["PYARROW_ALLOCATOR"] = "system"

try:
    import pyarrow as pa
    pa.set_memory_pool(pa.system_memory_pool())
except Exception:
    pass

import streamlit as st



def main():
    """Main Streamlit Application Layout & Router."""
    from src.db import init_db
    from src.auth import render_auth_page
    from src.manager import render_manager_portal
    from src.sender import render_sender_portal

    st.set_page_config(
        page_title="WareVisor - Warehouse & Retail Portal",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )

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
