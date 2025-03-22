import os
import requests
import time
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from hashlib import sha256
from datetime import datetime, timedelta

LOG_RETENTION_DAYS = 30

class SimpleHTTPRequestHandlerNoLogs(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("/snap.jpeg"):
            # Allow access to snapshots without authentication
            camera_name = self.path.strip("/").split("/")[0]
            self._log_request(camera_name)
            super().do_GET()
        else:
            # Redirect all other requests to weather.com
            self.send_response(302)
            self.send_header("Location", "https://weather.com")
            self.end_headers()

    def _log_request(self, camera_name):
        log_file_path = f"/home/webservers/cameras/{camera_name}/log_file.log"
        ip = self.client_address[0]
        url = self.path
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"{timestamp} - IP: {ip}, URL: {url}\n"

        # Ensure logs are rotated based on retention period
        if os.path.exists(log_file_path):
            self._rotate_logs(log_file_path)
        with open(log_file_path, "a") as log_file:
            log_file.write(log_entry)

    def _rotate_logs(self, log_file_path):
        # Remove old entries beyond retention period
        retention_cutoff = datetime.now() - timedelta(days=LOG_RETENTION_DAYS)
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
        with open(log_file_path, "w") as log_file:
            for line in lines:
                try:
                    timestamp_str = line.split(" - ")[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    if timestamp >= retention_cutoff:
                        log_file.write(line)
                except ValueError:
                    pass  # Skip malformed lines

    def list_directory(self, path):
        # Disable directory listing entirely
        self.send_error(403, "Directory listing is forbidden")
        return None

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in separate threads."""

def setup():
    try:
        print("Raspberry Pi Camera Setup Wizard\n")

        # Gather necessary configuration
        local_ip = input("Enter the local IP address of this Raspberry Pi: ").strip()
        port = input("Enter the port you want the web server to run on (default: 8080): ").strip() or "8080"

        # Ask about the cameras
        num_cameras = int(input("\nEnter the number of cameras to configure: "))
        cameras = []

        for i in range(1, num_cameras + 1):
            print(f"\n--- Camera {i} Configuration ---")
            camera_name = input(f"Enter a name for Camera {i} (e.g., Camera001): ").strip()
            camera_url = input(f"Enter the URL for Camera {i} (e.g., http://192.168.1.10/snap.jpeg): ").strip()
            camera_path = f"/home/webservers/cameras/{camera_name}/"  # Directory for this camera
            cameras.append({
                "name": camera_name,
                "url": camera_url,
                "path": camera_path
            })

        # Return the full configuration
        return {
            "local_ip": local_ip,
            "port": port,
            "cameras": cameras
        }
    except Exception as e:
        print(f"Error during setup: {e}")
        return None

def generate_directories(cameras):
    print("\nCreating necessary directories...")
    for camera in cameras:
        if not os.path.exists(camera["path"]):
            os.makedirs(camera["path"])
            print(f"Created folder: {camera['path']}")

def fetch_image(camera):
    try:
        file_name = camera["url"].split("/")[-1] or "default_image.jpeg"  # Fallback file name
        save_path = os.path.join(camera["path"], file_name)

        # Fetch the image
        response = requests.get(camera["url"], timeout=10)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            print(f"{camera['name']}: Image updated successfully at {save_path}")
        else:
            print(f"{camera['name']}: Failed to fetch image. Status code: {response.status_code}")
    except Exception as e:
        print(f"{camera['name']}: Error fetching image. {e}")

def start_fetch_loop(cameras):
    print("\nStarting to fetch images from cameras...")
    while True:
        for camera in cameras:
            fetch_image(camera)
        time.sleep(1)  # Adjust the interval as needed

def start_http_server(ip, port):
    os.chdir("/home/webservers/cameras")
    server = ThreadedHTTPServer((ip, int(port)), SimpleHTTPRequestHandlerNoLogs)
    print(f"Starting server at {ip}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")

if __name__ == "__main__":
    config = setup()

    if config:
        generate_directories(config["cameras"])

        with open("/home/webservers/config.json", "w") as config_file:
            json.dump(config, config_file, indent=4)

        start_server = input("Start the web server? (yes/no): ").strip().lower() == "yes"
        if start_server:
            from threading import Thread
            Thread(target=start_fetch_loop, args=(config["cameras"],), daemon=True).start()
            start_http_server(config["local_ip"], config["port"])
    else:
        print("Setup failed. Please restart the script.")
