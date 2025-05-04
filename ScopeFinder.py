import requests
import json
import time
import os
from urllib.parse import urlparse
from colorama import Fore, Style


print(Fore.RED + """
███████╗ ██████╗ ██████╗ ██████╗ ███████╗     ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗
██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔════╝     ██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗
███████╗██║     ██║   ██║██████╔╝█████╗ """+ Fore.WHITE+ '█████' +Fore.RED+""" █████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝
╚════██║██║     ██║   ██║██╔═══╝ ██╔══╝       ██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗
███████║╚██████╗╚██████╔╝██║     ███████╗     ██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║
╚══════╝ ╚═════╝ ╚═════╝ ╚═╝     ╚══════╝     ╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝
""" + Style.RESET_ALL)

# configs
DISCORD_WEBHOOK_URL = "<Your discord webhook>" #replace whit your discord webhook
H1_GITHUB_URL = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/hackerone_data.json"
BUGCROWD_URL = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/refs/heads/main/data/bugcrowd_data.json"
H1_SEEN_FILE = "seen_h1.json"
BUGCROWD_SEEN_FILE = "seen_bugcrowd.json"
HACKERONE_LINK = "https://hackerone.com/"
BUGCROWD_LINK = "https://bugcrowd.com/engagements/"


def extract_root_domain(url):
    try:
        parsed = urlparse(url if url.startswith("http") else "http://" + url)
        parts = parsed.hostname.split(".")
        return ".".join(parts[-2:])
    except:
        return url


def load_seen_targets(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_targets(filename, targets):
    with open(filename, "w") as f:
        json.dump(list(targets), f)


def fetch_json(url):
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"❌Error fetching from {url}: {e}")
        return []


# read programs
def parse_hackerone(data):
    targets = {}
    for program in data:
        name = program.get("name", "Unknown Program")
        handle = program.get("handle", "")
        for target in program.get("targets", {}).get("in_scope", []):
            asset = target.get("asset_identifier")
            if asset and target.get("asset_type") == "URL":
                unique_key = f"HackerOne-{handle}-{asset}"
                root = extract_root_domain(asset)
                targets[unique_key] = {
                    "display_root": root,
                    "program_name": name,
                    "asset_identifier": asset,
                    "asset_type": target.get("asset_type", "N/A"),
                    "availability_requirement": target.get(
                        "availability_requirement", "N/A"
                    ),
                    "confidentiality_requirement": target.get(
                        "confidentiality_requirement", "N/A"
                    ),
                    "eligible_for_bounty": target.get("eligible_for_bounty", False),
                    "eligible_for_submission": target.get(
                        "eligible_for_submission", False
                    ),
                    "instruction": target.get("instruction", "N/A"),
                    "integrity_requirement": target.get("integrity_requirement", "N/A"),
                    "max_severity": target.get("max_severity", "N/A"),
                    "program_handle": handle,
                    "platform": "HackerOne",
                }
    return targets


def parse_bugcrowd(data):
    targets = {}
    for program in data:
        name = program.get("name", "Unknown Program")
        link = program.get("url", "")
        handle = link.split("/")[-1] if link else ""
        for target in program.get("targets", {}).get("in_scope", []):
            if target.get("type") == "website":
                asset = target.get("target")
                unique_key = f"Bugcrowd-{handle}-{asset}"
                root = extract_root_domain(asset)
                targets[unique_key] = {
                    "display_root": root,
                    "program_name": name,
                    "asset_identifier": asset,
                    "asset_type": "website",
                    "availability_requirement": "N/A",
                    "confidentiality_requirement": "N/A",
                    "eligible_for_bounty": True if program.get("max_payout") else False,
                    "eligible_for_submission": True,
                    "instruction": "N/A",
                    "integrity_requirement": "N/A",
                    "max_severity": "N/A",
                    "program_handle": handle,
                    "platform": "Bugcrowd",
                    "max_payout": program.get("max_payout", None),
                }
    return targets


# Discord embed
def send_embed_to_discord(asset_identifier, info):
    severity_colors = {
        "low": 0x00FF99,
        "medium": 0xFFCC00,
        "high": 0xFF6600,
        "critical": 0xFF0000,
    }

    sev = info.get("max_severity", "none").lower()
    color = severity_colors.get(sev, 0xAAAAAA)

    bounty_status = (
        "🏴‍☠️ Bounty Available" if info.get("eligible_for_bounty") else "❌ No Bounty"
    )
    submission_status = (
        "📤 Submission Allowed"
        if info.get("eligible_for_submission")
        else "🔒 VDP Only"
    )

    platform = info.get("platform")
    handle = info.get("program_handle", "")
    if platform == "HackerOne":
        program_link = (
            f"[**{info.get('program_name')}**]({HACKERONE_LINK}{handle}?type=team)"
        )
        footer = (
            f"HackerOne - [View All Programs](https://hackerone.com/opportunities/all)"
        )
    else:
        program_link = f"[**{info.get('program_name')}**]({BUGCROWD_LINK}{handle})"
        footer = f"Bugcrowd - [View All Programs](https://bugcrowd.com/programs)"

    fields = [
        {"name": "📦 Program", "value": program_link, "inline": False},
        {
            "name": "🌐 Asset",
            "value": info.get("asset_identifier", "N/A"),
            "inline": False,
        },
        {"name": "📌 Type", "value": info.get("asset_type", "N/A"), "inline": True},
        {"name": "🔐 Max Severity", "value": sev.capitalize(), "inline": True},
        {"name": "💰 Bounty Status", "value": bounty_status, "inline": True},
        {"name": "📨 Submission Status", "value": submission_status, "inline": True},
        {
            "name": "📡 Availability",
            "value": str(info.get("availability_requirement", "N/A") or "N/A"),
            "inline": True,
        },
        {
            "name": "🔒 Confidentiality",
            "value": str(info.get("confidentiality_requirement", "N/A") or "N/A"),
            "inline": True,
        },
        {
            "name": "🧱 Integrity",
            "value": str(info.get("integrity_requirement", "N/A") or "N/A"),
            "inline": True,
        },
    ]

    if info["platform"] == "Bugcrowd" and info.get("max_payout"):
        fields.append(
            {"name": "💸 Max Payout", "value": f"${info['max_payout']}", "inline": True}
        )

    fields.append(
        {
            "name": "📘 Program Instructions",
            "value": info.get("instruction") or "N/A",
            "inline": False,
        }
    )
    fields.append({"name": "🏁 Platform", "value": footer, "inline": False})

    embed = {"title": "New Target Detected!", "color": color, "fields": fields}
    payload = {"embeds": [embed]}

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print(Fore.CYAN + f"✅ Sent New Target: {asset_identifier}")
    except Exception as e:
        print(Fore.RED + f"❌ Error sending to Discord: {e}")


if __name__ == "__main__":
    print(Fore.GREEN + "Monitoring Bug Bounty Targets...")
    seen_h1 = load_seen_targets(H1_SEEN_FILE)
    seen_bc = load_seen_targets(BUGCROWD_SEEN_FILE)
    first_run = not (seen_h1 or seen_bc)

    while True:
        h1_data = fetch_json(H1_GITHUB_URL)
        bc_data = fetch_json(BUGCROWD_URL)

        h1_targets = parse_hackerone(h1_data)
        bc_targets = parse_bugcrowd(bc_data)

        new_h1 = {k: v for k, v in h1_targets.items() if k not in seen_h1}
        new_bc = {k: v for k, v in bc_targets.items() if k not in seen_bc}

        if new_h1 or new_bc:
            for asset_id, info in sorted({**new_h1, **new_bc}.items(), reverse=True):
                if not first_run:
                    send_embed_to_discord(asset_id, info)
                else:
                    print(f"Skipping initial send for: {asset_id}")

                if info["platform"] == "HackerOne":
                    seen_h1.add(asset_id)
                elif info["platform"] == "Bugcrowd":
                    seen_bc.add(asset_id)

            save_seen_targets(H1_SEEN_FILE, seen_h1)
            save_seen_targets(BUGCROWD_SEEN_FILE, seen_bc)
        else:
            print(Fore.YELLOW + "⏳ No new targets found.")

        first_run = False
        time.sleep(1800) #30min
