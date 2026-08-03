import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080

def run():
    web_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_dir)
    
    Handler = http.server.SimpleHTTPRequestHandler
    
    print("==================================================")
    print("WareVisor Manager Dashboard Server Started!")
    print(f"URL: http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    print("==================================================")
    
    try:
        webbrowser.open(f"http://localhost:{PORT}")
    except Exception:
        pass
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped gracefully.")

if __name__ == "__main__":
    run()
