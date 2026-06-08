# Android Registration — Automated Test Guide

## What this script does

This script launches the **Furgechat Android app** on a connected emulator,
taps **"No account? Register here"** to open the registration screen, fills in a
brand-new, unique email and a password, taps **Register Account**, and then
proves it worked by waiting for the **"Registration Approved! You can now log
in."** message to appear. If that message shows up it prints **[PASS]** (with how
long it took); if anything goes wrong it prints **[FAIL]**, saves a screenshot,
and exits with an error code.

---

## Acceptance criteria (from the assessment PDF)

> **Registration:** Develop a script that registers a new user account.

This test satisfies that requirement by creating a unique account each run and
confirming the app's "Registration Approved!" message.

---

## Prerequisites

You need these installed and running **before** you start:

- **Python 3.11 or newer.**
- **JDK 17** (required by the Android tooling).
- **Android SDK** with **`ANDROID_HOME`** set and `adb` on your PATH.
- **An Android emulator running** — this test targets `emulator-5554`
  (Pixel 10 Pro, Android 13). Start it from Android Studio's Device Manager.
- **Node.js** + the **Appium 2 server** running on port **4723**, with the
  **uiautomator2** driver installed:
  ```bash
  npm install -g appium
  appium driver install uiautomator2
  appium                       # starts the server on http://127.0.0.1:4723
  ```
- **The app file** present at `Assets/furgechat.apk` (relative to the repo root).

### How to verify the prerequisites

```bash
node -v                # e.g. v20.11.0  (Node is installed)
appium -v              # e.g. 2.5.4     (Appium server is installed)
adb devices            # must list:  emulator-5554   device
java -version          # must show version 17.x  (JDK 17)
```
```bat
:: Windows (Command Prompt) — confirm the SDK location is set
echo %ANDROID_HOME%
```
```powershell
# Windows (PowerShell)
echo $env:ANDROID_HOME
```

---

## Setup (one time)

Open a terminal **in this folder** (`Auth/Registration/Android`):

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

Then open **`credentials.json`** and set the test-account details. For this
assessment:

```json
{
  "apk_path": "Assets/furgechat.apk",
  "new_user": {
    "email_prefix": "qa_test",
    "email_domain": "buzzerfan.test",
    "password": "QaTest123!"
  }
}
```

The email is **generated fresh on every run** as
`qa_test_<unix-timestamp>@buzzerfan.test`, so each registration is unique. The
password is static and meets the app's "min 6 chars" rule.

`credentials.json` is git-ignored on purpose — only `credentials.example.json`
is committed.

---

## How to run

With the emulator booted, the Appium server running, and the virtual environment
active:

```bash
python main.py
```

> **There is no "headless" mode for Appium** — it drives the real emulator
> screen, so you will see the app open, switch to the register screen, fill in,
> and show the approval message as it runs.

---

## Expected output

A successful run prints something like:

```
2026-06-08 10:02:01 | INFO     | android_register | Logging initialized. Writing to logs/android_register_20260608_100201.log
2026-06-08 10:02:01 | INFO     | android_register | Starting Android Registration test (Appium server http://127.0.0.1:4723).
2026-06-08 10:02:01 | INFO     | android_register | Generated unique email: qa_test_1812345721@buzzerfan.test
2026-06-08 10:02:14 | INFO     | android_register | Login screen loaded; tapping 'No account? Register here'.
2026-06-08 10:02:15 | INFO     | android_register | Registration screen loaded.
2026-06-08 10:02:16 | INFO     | android_register | Registering new account with email 'qa_test_1812345721@buzzerfan.test'.
2026-06-08 10:02:18 | INFO     | android_register | [PASS] Registration succeeded — success message appeared in 1.42s for 'qa_test_1812345721@buzzerfan.test'.
2026-06-08 10:02:19 | INFO     | android_register | Appium session closed.
```

- A full log of every run is saved in the **`logs/`** folder.
- On failure a screenshot is saved as **`screenshots/registration_failure_<timestamp>.png`**.
- Exit code is **0** on success and **1** on failure.

---

## Troubleshooting

**1. Success message never appears (timeout after 15s)**
The "Registration Approved!" message did not show within the wait window. Open
the screenshot in `screenshots/` to see what was on screen. Common causes: the
app was slow to respond (increase `timeouts.success_wait_seconds` in
`capabilities.json`), or the form was rejected for one of the reasons below.

**2. Email format rejected**
The default domain is `buzzerfan.test`. If the app validates against real
domains it may reject that address and stay on the form. Change
`new_user.email_domain` in `credentials.json` to a domain the app accepts (for
example `gmail.com`, as seen in the Inspector) and run again.

**3. "Duplicate email" if the timestamp collides**
The generated email uses a **per-second** Unix timestamp
(`qa_test_<seconds>@…`). If you launch two runs within the same second — or the
app already has an account from a previous run at that exact second — the second
attempt can be rejected as a duplicate. Simply re-run (the next second yields a
new address). For very rapid repeated runs, raise the timestamp resolution in
`utils/test_data.py` (e.g. use `time.time_ns()`).

**4. Wrong field gets filled / Flutter element changed**
This is a **Flutter** app, so the email and password fields have no stable id —
they are located by **position** (`EditText` instance 0 and instance 1). If the
form layout changes, those positions can shift. The script already warns if a
field's placeholder label does not match what is expected (a sign the layout
moved). To fix: open the screen in **Appium Inspector**, re-capture the email
field, password field, and Register button, and update the locators in
`pages/register_page.py`.

---

## Files in this folder

| File | Purpose |
|------|---------|
| `main.py` | The test flow — what to do, in order. |
| `pages/login_page.py` | The login screen's "Register here" link. |
| `pages/register_page.py` | The registration form + success message. |
| `pages/base_page.py` | Shared device actions (waits, typing, tapping). |
| `utils/driver_factory.py` | Loads config, resolves the APK path, starts Appium. |
| `utils/logger.py` | Writes logs to the screen and to `logs/`. |
| `utils/test_data.py` | Generates the unique email address. |
| `capabilities.json` | Static Appium settings (server, timeouts, capabilities). |
| `credentials.example.json` | Template for your private `credentials.json`. |
| `requirements.txt` | Pinned Python packages to install. |
| `.gitignore` | Keeps `credentials.json`, `screenshots/`, `logs/` out of git. |
