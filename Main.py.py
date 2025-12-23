import subprocess
import sys
import importlib
import os
import re

# Function to check and install libraries
def check_and_install_libraries():
    """Check if required libraries are installed; install them if missing."""
    required_libraries = {
        'requests': 'requests==2.31.0',
        'bs4': 'beautifulsoup4==4.12.3',
        'pandas': 'pandas==2.0.3',
        'gspread': 'gspread==5.12.0',
        'oauth2client': 'oauth2client==4.1.3'
    }
    installed_any = False
    
    # Check if pip is available
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', '--version'])
    except subprocess.CalledProcessError:
        print("Error: Pip is not available. Please install pip manually.")
        sys.exit(1)
    
    print("Checking for required libraries...")
    for module_name, pip_name in required_libraries.items():
        try:
            importlib.import_module(module_name)
            print(f"{module_name} is already installed.")
        except ImportError:
            print(f"{module_name} not found. Installing {pip_name}...")
            try:
                # Use --user flag to avoid permission issues
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_name, '--user'])
                print(f"Successfully installed {pip_name}.")
                installed_any = True
            except subprocess.CalledProcessError as e:
                print(f"Error: Failed to install {pip_name}: {e}")
                sys.exit(1)
    
    if installed_any:
        print("Some libraries were installed. Please rerun the script to ensure all libraries are loaded.")
        sys.exit(0)

# Run library check and installation
check_and_install_libraries()

#import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# List of game URLs
urls = [
    "https://stats.ncaa.org/contests/5336663/individual_stats",
    "https://stats.ncaa.org/contests/5336814/individual_stats",
    "https://stats.ncaa.org/contests/5336815/individual_stats"
]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

#create web scraper
def scrape_game_box_score(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    tables = soup.find_all("table")
    
    player_data = []
    #get game id from the URL 
    game_id = re.search(r'contests/(\d+)/individual_stats', url).group(1)
    for table in tables:
        if 'AB' in table.text:
            #team_name = table.find_previous("h4").get_text(strip=True)
            rows = table.find_all("tr")[1:-1]  # skip header row

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 11:  # ensure it's a valid player row
                    player_name = cols[1].get_text(strip=True)
                    ab = cols[4].get_text(strip=True)
                    r = cols[3].get_text(strip=True)
                    h = cols[5].get_text(strip=True)
                    hr = cols[9].get_text(strip=True)
                    rbi = cols[10].get_text(strip=True)
                    
                    player_data.append({
                        "Game_ID": game_id,
                        "Player": player_name,
                        "AB": ab,
                        "R": r,
                        "H": h,
                        "HR": hr,
                        "RBI": rbi
                        
                    })
    
    return pd.DataFrame(player_data)

# Combine all games
all_games_df = pd.concat([scrape_game_box_score(url) for url in urls], ignore_index=True)
print(all_games_df.columns)


MASTER_TOKEN = os.getenv("TRUMEDIA_MASTER_TOKEN")
if not MASTER_TOKEN:
    raise RuntimeError("TRUMEDIA_MASTER_TOKEN environment variable not set")



# Step 1: Get temporary token
temp_token_response = requests.get(
    "https://project.trumedianetworks.com/api/token",
    headers={"apiKey": MASTER_TOKEN}
)

temp_token = temp_token_response.json().get("token")

# Step 2: Get the player lookup table
lookup_response = requests.get(
    "https://project.trumedianetworks.com/api/ncaa/ncaa-baseball-players/0",  
    headers={"tempToken": temp_token}
)

lookup_df = pd.DataFrame(lookup_response.json())
#create a subset dataframe with only player name and ID
lookup_subset = lookup_df[['fullName', 'playerId']]

#Remove special characters and convert names to lowercase for merging
all_games_df['Player'] = all_games_df['Player'].str.lower().str.strip()
lookup_subset['fullName'] = lookup_subset['fullName'].str.lower().str.strip()

#Merge all games df and api lookup subset dataframes
merged_df = pd.merge(
    all_games_df,           
    lookup_subset,              
    how="left",
    left_on="Player",
    right_on="fullName"    
)
print(merged_df)



# Define scope and credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CREDS_PATH")
if not GOOGLE_CREDS_PATH:
    raise RuntimeError("GOOGLE_CREDS_PATH environment variable not set")

creds = ServiceAccountCredentials.from_json_keyfile_name(
    GOOGLE_CREDS_PATH, scope)

# Authorize client
client = gspread.authorize(creds)

# Open the sheet by name (or URL or key)
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
if not GOOGLE_SHEET_ID:
    raise RuntimeError("GOOGLE_SHEET_ID environment variable not set")

sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1


# Prepare data (replace with your final DataFrame)
final_df = merged_df[["Game_ID", "Player", "playerId", "R", "AB", "H", "HR", "RBI"]]

# Clear old data
sheet.clear()

# Push headers and data
sheet.update([final_df.columns.values.tolist()] + final_df.values.tolist())
