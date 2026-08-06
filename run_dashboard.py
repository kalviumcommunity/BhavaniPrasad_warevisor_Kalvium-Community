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
    print("WareVisor RetailStock Manager Server Started!")
    print(f"Login Portal URL: http://localhost:{PORT}/login.html")
    print(f"Dashboard URL: http://localhost:{PORT}/index.html")
    print("Press Ctrl+C to stop.")
    print("==================================================")
    
    try:
        webbrowser.open(f"http://localhost:{PORT}/login.html")
    except Exception:
        pass
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped gracefully.")

if __name__ == "__main__":
    run()
