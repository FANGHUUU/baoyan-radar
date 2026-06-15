"""Push camps.json to GitHub via API (bypasses GFW git block)."""
import urllib.request, json, base64, os

REPO = "FANGHUUU/baoyan-radar"
FILE_PATH = "data/camps.json"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".ghtoken")
CAMPS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "camps.json")

def api(url, method="GET", data=None):
    token = open(TOKEN_FILE).read().strip()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "baoyan-radar-bot"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())

def main():
    # 1. Get current file SHA
    url = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
    current = api(url)
    sha = current["sha"]

    # 2. Read local camps.json
    with open(CAMPS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # 3. Push via API
    camp_count = len(json.loads(content).get("camps", []))
    active = sum(1 for c in json.loads(content).get("camps", []) if not c.get("expired"))
    commit_msg = f"update: daily camp refresh - {active} active camps ({camp_count} total)"
    payload = {
        "message": commit_msg,
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha,
        "branch": "main"
    }
    result = api(url, method="PUT", data=payload)
    print(f"Pushed! Commit: {result['commit']['sha'][:7]} - {result['commit']['message']}")

if __name__ == "__main__":
    main()
