"""Push all project files to GitHub via API (bypasses GFW git block)."""
import urllib.request, json, base64, os

TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "..", ".ghtoken")
REPO = "FANGHUUU/baoyan-radar"
BASE = os.path.join(os.path.dirname(__file__), "..")

EXCLUDE_DIRS = {".git", "node_modules", "logs", "daily-reports", "__pycache__", "scripts"}
EXCLUDE_FILES = {".ghtoken"}

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

def collect_files():
    result = []
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f in EXCLUDE_FILES:
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, BASE).replace("\\", "/")
            result.append((rel, full))
    return result

def main():
    files = collect_files()
    print(f"Pushing {len(files)} files via GitHub API...")

    for rel, full in sorted(files):
        url = f"https://api.github.com/repos/{REPO}/contents/{rel}"

        sha = None
        try:
            existing = api(url)
            sha = existing.get("sha")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                pass  # new file
            else:
                print(f"  SKIP {rel}: HTTP {e.code}")
                continue

        with open(full, "rb") as fh:
            raw = fh.read()
        content_b64 = base64.b64encode(raw).decode()

        payload = {
            "message": f"feat: add {rel}",
            "content": content_b64,
            "branch": "main"
        }
        if sha:
            payload["sha"] = sha
            payload["message"] = f"update: {rel}"

        try:
            result = api(url, method="PUT", data=payload)
            print(f"  OK  {rel}")
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"  FAIL {rel}: {e.code} {body[:200]}")
            return

    print(f"Done! View at https://github.com/{REPO}")

if __name__ == "__main__":
    main()
