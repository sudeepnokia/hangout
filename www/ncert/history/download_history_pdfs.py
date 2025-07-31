
import requests
import os

# The directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# The directory to save the PDFs in
output_dir = os.path.join(script_dir, "pdfs")

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# List of URLs for the chapters
urls = {
    "The French Revolution.pdf": "https://ncert.nic.in/textbook/pdf/iess301.pdf",
    "Socialism in Europe and the Russian Revolution.pdf": "https://ncert.nic.in/textbook/pdf/iess302.pdf",
    "Nazism and the Rise of Hitler.pdf": "https://ncert.nic.in/textbook/pdf/iess303.pdf",
    "Forest Society and Colonialism.pdf": "https://ncert.nic.in/textbook/pdf/iess304.pdf",
    "Pastoralists in the Modern World.pdf": "https://ncert.nic.in/textbook/pdf/iess305.pdf",
}

# Download each chapter
for filename, url in urls.items():
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()  # Raise an exception for bad status codes
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded {filename} to {file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

print("All chapters downloaded.")
