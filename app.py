import requests
from socialscan.util import sync_execute_queries
from socialscan.platforms import Platforms

# === Custom checkers for GitHub & YouTube ===

def check_github(username):
    try:
        r = requests.get(f"https://github.com/{username}", timeout=5)
        return r.status_code == 404  # 404 = available
    except:
        return None

def check_youtube(username):
    try:
        r = requests.get(f"https://www.youtube.com/@{username}", timeout=5)
        return r.status_code == 404  # 404 = available
    except:
        return None

# === User input ===
raw_input = input("enter usernames to check (comma-separated): ")
usernames = [u.strip() for u in raw_input.split(",") if u.strip()]

# === socialscan (twitter, insta, reddit) ===
scan_platforms = [Platforms.TWITTER, Platforms.INSTAGRAM, Platforms.REDDIT]
scan_results = sync_execute_queries(usernames, scan_platforms)

# === organize results ===
availability = {user: {} for user in usernames}
for res in scan_results:
    status = "Available" if res.available else "Taken"
    availability[res.query][str(res.platform).lower()] = status

# === run GitHub + YouTube checks ===
for user in usernames:
    gh = check_github(user)
    yt = check_youtube(user)
    availability[user]["github"] = "Available" if gh else "Taken" if gh == False else "Error"
    availability[user]["youtube"] = "Available" if yt else "Taken" if yt == False else "Error"

# === print results ===
print("\n🔍 username availability check:\n")
for user in usernames:
    print(f"— {user}")
    for platform, status in availability[user].items():
        print(f"   {platform.capitalize()}: {status}")
    print()