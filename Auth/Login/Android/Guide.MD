# Android Login — Automated Test Guide

## What this script does

This script launches the **Furgechat Android app** on a connected emulator,
types the default username and password shown on the login screen, taps
**Login**, and then proves the login worked by waiting for the **"All Messages
Dashboard"** screen to appear. If the dashboard shows up it prints **[PASS]**
(with how many seconds it took); if anything goes wrong it prints **[FAIL]**,
saves a screenshot of what was on screen, and exits with an error code.

---

## Prerequisites

You need these installed and running **before** you start:

- **Python 3.11 or newer.**
- **JDK 17** (required by the Android tooling).
- **Android SDK** with the **`ANDROID_HOME`** environment variable set, and
  `adb` available on your PATH.
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

Run each command and confirm it gives a sensible answer:

```bash
node -v                # e.g. v20.11.0  (Node is installed)
appium -v              # e.g. 2.5.4     (Appium server is installed)
adb devices            # must list:  emulator-5554   device
java -version          # must show version 17.x  (JDK 17)
```

Check `ANDROID_HOME` is set:

```bat
:: Windows (Command Prompt)
echo %ANDROID_HOME%
```
```powershell
# Windows (PowerShell)
echo $env:ANDROID_HOME
```
```bash
# macOS / Linux
echo $ANDROID_HOME
```

If any command fails or prints nothing, fix that item before continuing (see
Troubleshooting).

---

## Setup (one time)

Open a terminal **in this folder** (`Auth/Login/Android`):

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

Then open **`credentials.json`** and fill in the values. For this assessment the
defaults shown in the app are:

```json
{
  "apk_path": "Assets/furgechat.apk",
  "username": "admin",
  "password": "password123"
}
```

`credentials.json` is git-ignored on purpose — it is your private copy. Only
`credentials.example.json` is committed.

---

## How to run

With the emulator booted, the Appium server running, and the virtual environment
active:

```bash
python main.py
```

> **There is no "headless" mode for Appium** — it drives the real emulator
> screen, so you will see the app open and the fields fill in as it runs. Keep
> the emulator window visible.

---

## Expected output

A successful run prints something like:

```
2026-06-08 09:46:02 | INFO     | android_login | Logging initialized. Writing to logs/android_login_20260608_094602.log
2026-06-08 09:46:02 | INFO     | android_login | Starting Android Login test (Appium server http://127.0.0.1:4723).
2026-06-08 09:46:15 | INFO     | android_login | Login screen loaded.
2026-06-08 09:46:15 | INFO     | android_login | Entering credentials for user 'admin' and tapping Login.
2026-06-08 09:46:18 | INFO     | android_login | [PASS] Login succeeded — 'All Messages Dashboard' appeared in 1.84s.
2026-06-08 09:46:19 | INFO     | android_login | Appium session closed.
```

- A full log of every run is saved in the **`logs/`** folder.
- On failure a screenshot is saved as **`screenshots/login_failure_<timestamp>.png`**.
- Exit code is **0** on success and **1** on failure.

---

## Troubleshooting

**1. "ANDROID_HOME not set" (or `adb` not found)**
The Android SDK location is not exported. Set `ANDROID_HOME` to your SDK path
and add its `platform-tools` folder to PATH, then restart the terminal:
- Windows: set a User Environment Variable `ANDROID_HOME` =
  `C:\Users\<you>\AppData\Local\Android\Sdk`, and add
  `%ANDROID_HOME%\platform-tools` to PATH.
- macOS/Linux: add to your shell profile —
  `export ANDROID_HOME="$HOME/Library/Android/sdk"` (mac) or
  `export ANDROID_HOME="$HOME/Android/Sdk"` (linux), then
  `export PATH="$PATH:$ANDROID_HOME/platform-tools"`.
Verify with `adb devices`.

**2. "Could not find a connected Android device"**
No emulator/device is running. Start the emulator from Android Studio's Device
Manager and wait until it is fully booted, then run `adb devices` and confirm
`emulator-5554` is listed as `device`. If your emulator has a different id,
update `capabilities.appium:deviceName` in `capabilities.json`.

**3. "Connection refused on port 4723"**
The Appium server is not running. In a separate terminal run `appium` and leave
it open; confirm it says it is listening on `http://127.0.0.1:4723`. Confirm the
uiautomator2 driver is installed with `appium driver list --installed`.

**4. Element not found / Flutter element changed**
This is a **Flutter** app, so the username and password fields have no stable id
— they are located by **position** (`EditText` instance 0 and instance 1). If
the login form's layout changes, those positions can shift and the test will
fail to find the right field. The script already warns if a field's hint text
does not match what is expected (a sign the layout moved). To fix:
1. Open the screen in **Appium Inspector**.
2. Re-capture the username field, password field, and Login button.
3. Update the locators in `pages/login_page.py` (and the dashboard header in
   `pages/dashboard_page.py` if that screen changed).

---

## Files in this folder

| File | Purpose |
|------|---------|
| `main.py` | The test flow — what to do, in order. |
| `pages/login_page.py` | Login screen locators/actions + hint verification. |
| `pages/dashboard_page.py` | The post-login dashboard (assertion target). |
| `pages/base_page.py` | Shared device actions (waits, typing, tapping). |
| `utils/driver_factory.py` | Loads config, resolves the APK path, starts Appium. |
| `utils/logger.py` | Writes logs to the screen and to `logs/`. |
| `capabilities.json` | Static Appium settings (server, timeouts, capabilities). |
| `credentials.example.json` | Template for your private `credentials.json`. |
| `requirements.txt` | Pinned Python packages to install. |
| `.gitignore` | Keeps `credentials.json`, `screenshots/`, `logs/` out of git. |
