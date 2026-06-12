import os
import urllib.request

DATA_DIR = "data"

def download_sample_images():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    images = [
        {
            "url": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?auto=format&fit=crop&w=800",
            "name": "sample_car_1.jpg"
        }
    ]
    
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
    urllib.request.install_opener(opener)
    
    for img in images:
        filepath = os.path.join(DATA_DIR, img['name'])
        if not os.path.exists(filepath):
            try:
                print(f"Downloading {img['name']}...")
                urllib.request.urlretrieve(img['url'], filepath)
                print(f"Saved to {filepath}")
            except Exception as e:
                print(f"Failed to download {img['url']}: {e}")
        else:
            print(f"{img['name']} already exists.")

if __name__ == "__main__":
    download_sample_images()
