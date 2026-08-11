"""Dashboard launcher utility module."""

import os
import sys
import socket
import subprocess

DEFAULT_PORT = 8501

def find_available_port(start_port: int = 8501, max_attempts: int = 20) -> int:
    """Find an open port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                continue
    return start_port

def run():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root_dir)
    app_path = os.path.join(root_dir, "app.py")

    port = find_available_port(DEFAULT_PORT)

    print("==================================================")
    print("WareVisor RetailStock Manager Application Starting!")
    print(f"Login & Dashboard Portal URL: http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    print("==================================================")

    cmd = [
        sys.executable,
        "-m", "streamlit", "run", app_path,
        f"--server.port={port}",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped gracefully.")

if __name__ == "__main__":
    run()
