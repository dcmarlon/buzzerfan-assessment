# Android Chats — Automated Test Guide

## What this script does

This script launches the **Furgechat Android app** on a connected emulator, logs
in as **admin**, waits for the **"All Messages Dashboard"** to appear, then reads
and prints every chat shown on it. It skips dashboard controls that are not chats
(like the Logout icon), prints a final count, and finishes with **[PASS]** if at
least one chat was found. If anything goes wrong it prints **[FAIL]**, saves a
screenshot, and exits with an error code.

---

## Acceptance criteria (from the assessment PDF)

> **Chats:** Develop a script that prints all the visible chats under the
> "All Messages Dashboard" page, once logged into the admin account.

---

## A note on the chat text

On Android each chat row exposes a single **content-desc** that fuses the
contact name and the last message together with no separator, e.g.
`John Doe Almost done, fixing a cache bug.` Because there is no reliable way to
know where the name ends and the message begins (names can be one, two, or more
words), the script prints the **raw content-desc** for each chat. This fully
satisfies the requirement ("prints all the visible chats") without guessing a
split that could be wrong.

---

## Prerequisites

- **Python 3.11 or newer.**
- **JDK 17** (required by the Android tooling).
- **Android SDK** with **`ANDROID_HOME`** set and `adb` on your PATH.
- **An Android emulator running** — this test targets `emulator-5554`
  (Pixel 10 Pro, Android 13).
- **Node.js** + the **Appium 2 server** on port **4723** with the **uiautomator2**
  driver installed:
  ```bash
  npm install -g appium
  appium driver install uiautomator2
  appium                       # starts the server on http://127.0.0.1:4723
  ```
- **The app file** present at `Assets/furgechat.apk` (relative to the repo root).

### How to verify the prerequisites

```bash
node -v                # Node is installed
appium -v              # Appium server is installed
adb devices            # must list:  emulator-5554   device
java -version          # must show version 17.x
```
```bat
:: Windows (Command Prompt)
echo %ANDROID_HOME%
```
```powershell
# Windows (PowerShell)
echo $env:ANDROID_HOME
```

---

## Setup (one time)

In a terminal **in this folder** (`Chat/Chats/Android`):

### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item credentials.example.json credentials.json
```

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp credentials.example.json credentials.json
```

Then open **`credentials.json`** and set the login details (defaults for this
assessment):

```json
{
  "apk_path": "Assets/furgechat.apk",
  "username": "admin",
  "password": "password123"
}
```

`credentials.json` is git-ignored — only `credentials.example.json` is committed.

---

## How to run

With the emulator booted, the Appium server running, and the virtual environment
active:

```bash
python main.py
```

> **There is no "headless" mode for Appium** — it drives the real emulator
> screen, so you will see the app log in and the dashboard appear as it runs.

---

## Expected output

```
2026-06-08 12:14:01 | INFO     | android_chats | Logging initialized. Writing to logs/android_chats_20260608_121401.log
2026-06-08 12:14:01 | INFO     | android_chats | Starting Android Chats test (Appium server http://127.0.0.1:4723).
2026-06-08 12:14:16 | INFO     | android_chats | Logged in as admin
2026-06-08 12:14:16 | INFO     | android_chats | Dashboard loaded
2026-06-08 12:14:16 | INFO     | android_chats | Skipped non-chat button: Logout
2026-06-08 12:14:16 | INFO     | android_chats | Chats visible on dashboard:
2026-06-08 12:14:16 | INFO     | android_chats |   1. John Doe Almost done, fixing a cache bug.
2026-06-08 12:14:16 | INFO     | android_chats |   2. QA Lead Build failed on pipeline, check log files.
2026-06-08 12:14:16 | INFO     | android_chats | Found 2 chats
2026-06-08 12:14:17 | INFO     | android_chats | [PASS] Chats listing completed in 5.1s
2026-06-08 12:14:18 | INFO     | android_chats | Appium session closed.
```

- A full log of every run is saved in the **`logs/`** folder.
- On failure a screenshot is saved as **`screenshots/chats_failure_<timestamp>.png`**.
- Exit code is **0** on success and **1** on failure.

---

## Troubleshooting

**1. "No chat rows found" / zero chats returned (fails loud)**
The script logged in and reached the dashboard but found no chat buttons. Either
the chat-row selector broke (the app changed), or the signed-in account genuinely
has no chats. Open the screenshot in `screenshots/`, confirm you are logged in as
the expected account, and re-capture the chat-row button in Appium Inspector.

**2. content-desc parsing edge cases / an unexpected row appears**
The script prints each chat's raw content-desc and skips known non-chat controls
(currently just "Logout") plus any button with no content-desc. If a non-chat
button slips into the list (for example a "New Chat" floating button that has a
text label), copy its content-desc from the log line ("Skipped non-chat button:
…" shows what was ignored) and add it to `NON_CHAT_CONTENT_DESCS` in
`pages/dashboard_page.py`.

**3. Chat list / dashboard not loaded in time**
If you see "'All Messages Dashboard' did not load within 15s", login was slow or
failed. Confirm the credentials in `credentials.json`, make sure the emulator is
responsive, and if the device is just slow, increase
`timeouts.dashboard_wait_seconds` in `capabilities.json`.

---

## Files in this folder

| File | Purpose |
|------|---------|
| `main.py` | The test flow — log in, read chats, print them. |
| `pages/login_page.py` | The login screen (reused from the Login feature). |
| `pages/dashboard_page.py` | The dashboard: header + reading/filtering chat rows. |
| `pages/base_page.py` | Shared device actions (waits, typing, tapping). |
| `utils/driver_factory.py` | Loads config, resolves the APK path, starts Appium. |
| `utils/logger.py` | Writes logs (and the chat list) to screen and `logs/`. |
| `capabilities.json` | Static Appium settings (server, timeouts, capabilities). |
| `credentials.example.json` | Template for your private `credentials.json`. |
| `requirements.txt` | Pinned Python packages to install. |
| `.gitignore` | Keeps `credentials.json`, `screenshots/`, `logs/` out of git. |
