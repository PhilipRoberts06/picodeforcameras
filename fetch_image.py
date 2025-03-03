import requests
import time

camera_url = "http://ip/snap.jpeg"  # Replace with actual local IP
save_path = "/var/www/html/camera/snap.jpeg"

while True:
    try:
        response = requests.get(camera_url)
        if response.status_code == 200:
            with open(save_path, "wb") as file:
                file.write(response.content)
            print("Image updated.")
        else:
            print(f"Failed to retrieve image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(1)  # Update every second
