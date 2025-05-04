![Visitors](https://visitor-badge.laobi.icu/badge?page_id=YourUsername.ScopeFinder)
</br>

# 🎯 Scope Finder

Scope Finder is a Python script that **monitors bug bounty program scopes** (from HackerOne and Bugcrowd) and **automatically sends new targets** to your Discord channel via webhook. Ideal for bug bounty hunters who want to stay ahead and catch new assets as soon as they're added.

![image](https://github.com/user-attachments/assets/b9ddbfff-ca4d-4209-b3dd-db8bf93a3f14)
</br>

## 🚀 Features

- Fetches scopes from HackerOne and Bugcrowd
- Detects **new in-scope targets** (URLs, websites)
- Sends **Discord embed notifications** with detailed info:
  - Program name & link
  - Asset identifier & type
  - Bounty & submission status
  - Max severity, availability, confidentiality, integrity requirements
  - Max payout (For Bugcrowd) 
</br>

## ⚙️ Setup

### Clone the repository, install requirements, set your Discord webhook, and run:

```bash
git clone https://github.com/FARBODxME/Bugbounty_ScopeFinder.git
cd Bugbounty_ScopeFinder
pip install -r requirements.txt
```
### Set your Discord webhook
```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
```
### Run the script:
```bash
python scope_finder.py
```
</br>

## 📝 How it works

- Downloads the latest HackerOne and Bugcrowd scope data.

- Compares with local JSON files (seen_h1.json and seen_bugcrowd.json) to track what you’ve already seen.

- If new targets are found, it sends a Discord embed and updates the JSON files.

 💡On the first run, it skips sending to Discord (to avoid spam) but saves all data for future comparisons.
</br> </br>

## 📸 Example Discord Embed:
![image](https://github.com/user-attachments/assets/cf390c54-612e-4eb0-8714-85f9d4fdc15a)
</br> </br>

## ❗Notes
- Make sure your webhook URL is kept secret.

- The script persists state using JSON files (seen_h1.json, seen_bugcrowd.json), so don’t delete them unless you want to reset history.

- No database needed – simple & lightweight.
***
Happy hacking! 🏴‍☠️ 
omidvaram be karetoon biad<3
