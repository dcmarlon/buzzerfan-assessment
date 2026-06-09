# Android New Chat — Automated Test Guide

## What this script does

This script launches the **Furgechat Android app** on a connected emulator, logs
in as **admin**, opens a brand-new direct message with a freshly generated
contact, and sends **3 messages** into that conversation — verifying each one
shows up in the thread. It finishes with **[PASS]** if all three messages were
confirmed; if anything goes wrong it prints **[FAIL]**, saves a screenshot, and
exits with an error code.

---

## Acceptance criteria (from the assessment PDF)

> **New Chat:** Create a new chat with any user and send some messages to them.

---

## ⚠️ The page's quirk: contact names must be letters-only

The app **rejects contact names that contain digits** — it shows
*"DM Creation Denied: '&lt;name&gt;' contains numbers"* and leaves the dialog open
without creating the chat. (This was the trap: a timestamp-based name like
`QaUser1717834567` is always rejected.)

This script therefore generates a **digit-free** contact name — it maps the
timestamp's digits to letters (`0`→`a` … `9`→`j`), e.g. `QaUserbhiajijgba`, so
each run still gets a unique, valid name. With a valid name, tapping **Create**
closes the dialog and the new chat appears on the dashboard; the script then
opens it and sends the three messages.

> Each message is verified the instant it is sent. The script does **not**
> re-check all three at the end, because the conversation auto-scrolls to the
> newest message and older bubbles scroll out of the visible UI tree.

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

In a terminal **in this folder** (`Chat/NewChat/Android`):

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

The contact name is **generated fresh on every run** as `QaUser<unix-timestamp>`,
so each run creates a distinct chat. The 3 messages are fixed test fixtures
defined in `main.py`.

`credentials.json` is git-ignored — only `credentials.example.json` is committed.

---

## How to run

With the emulator booted, the Appium server running, and the virtual environment
active:

```bash
python main.py
```

> **There is no "headless" mode for Appium** — it drives the real emulator
> screen, so you will see the dialog open, the contact get typed, and the
> messages send as it runs.

---

## Expected output

```
2026-06-08 12:35:01 | INFO     | android_new_chat | Logging initialized. Writing to logs/android_new_chat_20260608_123501.log
2026-06-08 12:35:01 | INFO     | android_new_chat | Starting Android New Chat test (Appium server http://127.0.0.1:4723).
2026-06-08 12:35:16 | INFO     | android_new_chat | Logged in as admin
2026-06-08 12:35:16 | INFO     | android_new_chat | Dashboard loaded — tapping new-chat FAB
2026-06-08 12:35:16 | INFO     | android_new_chat | New-chat FAB located via fallback: icon-only Button
2026-06-08 12:35:17 | INFO     | android_new_chat | Start New DM dialog visible
2026-06-08 12:35:17 | INFO     | android_new_chat | Creating chat with contact: QaUser1717834567
2026-06-08 12:35:18 | INFO     | android_new_chat | DM creation confirmed (toast detected)
2026-06-08 12:35:18 | INFO     | android_new_chat | Sending message 1/3: "Hello from Buzzerfan QA automation"
2026-06-08 12:35:19 | INFO     | android_new_chat | Message 1 verified in conversation (sent via send-button tap)
2026-06-08 12:35:19 | INFO     | android_new_chat | Sending message 2/3: "This is automated message 2"
2026-06-08 12:35:20 | INFO     | android_new_chat | Message 2 verified in conversation (sent via send-button tap)
2026-06-08 12:35:20 | INFO     | android_new_chat | Sending message 3/3: "Final test message"
2026-06-08 12:35:21 | INFO     | android_new_chat | Message 3 verified in conversation (sent via send-button tap)
2026-06-08 12:35:21 | INFO     | android_new_chat | [PASS] New chat created with QaUser1717834567 and 3 messages sent (12.6s)
2026-06-08 12:35:22 | INFO     | android_new_chat | Appium session closed.
```

- A full log of every run is saved in the **`logs/`** folder.
- On failure a screenshot is saved as **`screenshots/new_chat_failure_<timestamp>.png`**.
- Exit code is **0** on success and **1** on failure.

---

## Troubleshooting

**1. New-chat FAB not found (or the wrong thing gets tapped)**
The FAB's position depends on how many chats exist. The Inspector's selector
(`Button.instance(2)`) is only correct with exactly the two seeded chats; after
previous runs add more chats, that index points at a chat row instead. The
script handles this by preferring the **icon-only Button** (the FAB has no
content-desc, unlike chat rows and Logout) and falling back to the last Button.
If it still fails, open the dashboard in **Appium Inspector**, select the FAB,
and update `FAB_PRIMARY` / the fallbacks in `pages/dashboard_page.py`.

**2. Approval toast missed**
The "DM Creation Approved for …" toast only shows for a few seconds and may be
gone before Appium polls for it. This is **not** a failure — the script logs a
warning and continues, because the true success criteria is that the messages
send. If you want to catch it more reliably, increase
`timeouts.toast_wait_seconds` in `capabilities.json`.

**3. Send button mis-tapped (message doesn't send on tap)**
The send control was not captured in the Inspector, so the script first taps the
first Button on the chat screen, and if no message bubble appears it presses the
Android ENTER key instead — the log shows which strategy worked ("sent via …").
If neither works, the first Button may be something else (e.g. the back arrow).
Open the chat screen in **Appium Inspector**, find the real send control, and set
`SEND_BUTTON` in `pages/chat_page.py`.

**4. Messages typed but not sent**
Flutter EditText fields sometimes do not commit keystrokes before the next
action, so a tap "sends" an empty/partial message. The script guards against
this by waiting until the input's text matches what was typed **before** tapping
send (an explicit wait, not a fixed pause), and by re-checking for the message
bubble after sending. If you still see partial sends on a slow device, raise
`timeouts.message_verify_seconds` in `capabilities.json`.

---

## Files in this folder

| File | Purpose |
|------|---------|
| `main.py` | The test flow — log in, create DM, send & verify messages. |
| `pages/login_page.py` | The login screen (reused from the Login feature). |
| `pages/dashboard_page.py` | Dashboard header + robust new-chat FAB finder. |
| `pages/new_dm_dialog.py` | The "Start New DM" dialog + approval toast. |
| `pages/chat_page.py` | The conversation: send messages + verify bubbles. |
| `pages/base_page.py` | Shared device actions (waits, typing, tapping). |
| `utils/driver_factory.py` | Loads config, resolves the APK path, starts Appium. |
| `utils/logger.py` | Writes logs to the screen and to `logs/`. |
| `capabilities.json` | Static Appium settings (server, timeouts, capabilities). |
| `credentials.example.json` | Template for your private `credentials.json`. |
| `requirements.txt` | Pinned Python packages to install. |
| `.gitignore` | Keeps `credentials.json`, `screenshots/`, `logs/` out of git. |
