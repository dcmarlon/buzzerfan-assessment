# Web Login — Automated Test Guide

This folder contains an automated test that opens the **Furgechat web app** in a
real Chrome browser, logs in with a username and password, and confirms the
login worked. If anything goes wrong it takes a screenshot, writes a log file,
and reports a failure.

You do **not** need to be a programmer to run it — just follow the steps below.

---

## 1. What this test does (in plain English)

1. Opens Chrome and goes to the Furgechat web address.
2. Types the username and password into the login form.
3. Ticks the **"I am not a robot"** checkbox. (The login button stays greyed
   out, showing "Please wait...", until this is ticked — the test waits for it
   to become clickable rather than guessing with a fixed delay.)
4. Clicks the login button.
5. Confirms login worked by checking that the login form goes away.
6. Prints **LOGIN SUCCESSFUL** and stops — or, if it failed, prints a clear
   error, saves a screenshot, and stops with an error.

---

## 2. Acceptance criteria (from the assessment PDF)

> **Login:** Develop a script that logins into a user account (You can use the
> following credential for logging in `admin: password`).

This test satisfies that requirement by logging in with the `admin` / `password`
credentials from `credentials.json` and confirming success via a post-login
marker element on screen.

---

## 3. Prerequisites

Before you run the test you need:

- **Python 3.11 or newer** installed. Check with `python --version`.
- **Google Chrome** installed (any recent version). The test downloads the
  matching browser driver automatically — you do not install that yourself.
- **Network access** to the Furgechat address
  (`https://raspberrypi.peafowl-eagle.ts.net/...`). This is a private Tailscale
  address, so you must be on the correct VPN / Tailnet to reach it. Confirm by
  opening the address in Chrome manually first.

---

## 4. Setup (one time)

Open a terminal **in this folder** (`Auth/Login/WebApp`) and run:

### Windows (PowerShell)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`venv` is a private, throwaway Python environment so this test's packages do not
affect anything else on your machine.

---

## 5. Selectors — already filled in

The username field, password field, captcha checkbox, and login button have all
been read from the live page, so **the test is ready to run as-is**.

Two *optional* selectors in `pages/login_page.py` are still placeholders
(`SELECTOR_TBD_FROM_INSPECTOR`). You do **not** need them to run the test:

- `LOGGED_IN_MARKER` — fill in (from the page shown *after* logging in) only if
  you want a stronger success check on top of "the login form disappeared."
- `ERROR_MESSAGE` — fill in only if the app shows an error banner on a bad
  login, to make failure messages clearer.

---

## 6. How to run

With the virtual environment active (step 4):

```bash
python main.py
```

---

## 7. What to expect

A successful run prints something like:

```
2026-06-08 10:15:02 | INFO     | web_login | Logging initialized. Writing to logs/web_login_20260608_101502.log
2026-06-08 10:15:02 | INFO     | web_login | Starting Web Login test against https://raspberrypi.peafowl-eagle.ts.net/furgechat
2026-06-08 10:15:05 | INFO     | web_login | Opened app; submitting credentials for user 'admin'.
2026-06-08 10:15:07 | INFO     | web_login | LOGIN SUCCESSFUL for user 'admin'.
2026-06-08 10:15:08 | INFO     | web_login | Browser closed.
```

- A full log of every run is saved in the **`logs/`** folder.
- If the test fails, a screenshot is saved in the **`screenshots/`** folder with
  the time in its filename.
- The program's exit code is `0` on success and `1` on failure (useful for
  automated pipelines).

---

## 8. Troubleshooting — the 3 most likely failures

**1. The page never loads / `ERR_CONNECTION` / page-load timeout**
You are probably not on the network that can reach the private Tailscale
address. Connect to the correct VPN / Tailnet and confirm you can open
`https://raspberrypi.peafowl-eagle.ts.net/furgechat` manually in Chrome.

**2. `TimeoutException` waiting for the login button to become clickable**
The login button starts disabled ("Please wait...") and only enables after the
captcha is ticked and the app finishes initialising. If the app's "Please
wait..." delay is longer than the configured wait, increase
`timeouts.explicit_wait_seconds` in `credentials.json` and try again.

**3. "LOGIN FAILED — still on the login page"**
The credentials in `credentials.json` are wrong, or the captcha step did not
register. Confirm the username/password are `admin` / `password`, then open the
screenshot in `screenshots/` to see exactly what the app showed at the moment of
failure.

---

## 9. Files in this folder

| File | Purpose |
|------|---------|
| `main.py` | The test flow — what to do, in order. |
| `pages/login_page.py` | The login screen's fields/buttons and actions. |
| `pages/base_page.py` | Shared browser actions (waits, typing, clicking). |
| `utils/driver_factory.py` | Starts and configures Chrome. |
| `utils/config.py` | Reads settings from `credentials.json`. |
| `utils/logger.py` | Writes logs to the screen and to `logs/`. |
| `utils/screenshot.py` | Saves screenshots to `screenshots/` on failure. |
| `credentials.json` | The web address and login details. |
| `requirements.txt` | The Python packages to install. |
