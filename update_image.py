import requests
import time
import os

camera_url = "http://aveiashq.mycrestron.com:22222/snap.jpeg"  # The provided source URL
save_path = "C:\\WebServer Cam 1\\image\\snap.jpeg"  # Update this to your desired file path
folder_path = os.path.dirname(save_path)  # Extract the folder path

# Ensure the directory exists
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"Created missing folder: {folder_path}")

def fetch_image():
    try:
        # Fetch the image from the URL
        response = requests.get(camera_url, timeout=10)  # Add timeout for reliability
        if response.status_code == 200:
            # Save the image
            with open(save_path, "wb") as file:
                file.write(response.content)
            print("Image updated successfully.")
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching image: {e}")

if __name__ == "__main__":
    while True:
        fetch_image()
        time.sleep(1)  # Update every second