import os
import requests
from bs4 import BeautifulSoup

# Define the base directory where you want to save the PDFs
BASE_DIR = '/Users/colinjacobs/Desktop/fun/Capstone/Equitable-Energy/OCA/gas'

def download_pdf(url, year):
    # Combine the base directory with the year to create the path
    directory_path = os.path.join(BASE_DIR, year)
    # Create the directory if it does not exist
    os.makedirs(directory_path, exist_ok=True)
    
    # Get the filename from the URL
    filename = os.path.join(directory_path, url.split('/')[-1])
    
    # Download and save the PDF
    response = requests.get(url, verify=False)  # verify=False if you need to bypass SSL verification
    with open(filename, 'wb') as f:
        f.write(response.content)

def fetch_and_download_pdfs(base_url):
    response = requests.get(base_url, verify=False)  # verify=False if SSL issues
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)

    for link in links:
        href = link['href']
        if href.lower().endswith('.pdf'):
            try:
                # Attempt to extract the year from the URL
                year = href.split('/')[-2]  # Adjust based on the actual URL structure
                print(f"Downloading {href} to {year} folder")
                download_pdf(href if href.startswith('http') else base_url + href, year)
            except Exception as e:
                print(f"Failed to download {href}: {e}")

# Usage
base_url = 'https://www.oca.pa.gov/natural-gas-shopping-guide-archive/'
fetch_and_download_pdfs(base_url)
