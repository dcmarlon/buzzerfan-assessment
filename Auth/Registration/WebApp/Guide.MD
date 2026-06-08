# Web Registration — Automated Test Guide

This folder contains an automated test that opens the **Furgechat web app**,
fills in the "Create account" form with a brand-new, unique username and email,
submits it, and confirms the account was created. If anything goes wrong it
takes a screenshot, writes a log file, and reports a failure.

You do **not** need to be a programmer to run it — just follow the steps below.

---

## 1. What this test does (in plain English)

1. Opens Chrome and goes to the Furgechat **registration** page.
2. Invents a **unique** username and email using the current date and time
   (e.g. `qa_user_20260608_101502`), so the test can be run again and again
   without ever clashing with an account it created earlier.
3. Types the username, email, and password into the form.
4. Clicks **Create account**.
5. Confirms it worked by checking that the registration form goes away.
6. Prints **REGISTRATION SUCCESSFUL** and stops — or, if it failed, prints a
   clear error, saves a screenshot, and stops with an error.

---

## 2. Acceptance criteria (from the assessment PDF)

> **Registration:** Develop a script that creates a user account.

This test satisfies that requirement by generating a unique account and
submitting the registration form, then confirming the app accepted it.

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

Open a terminal **in this folder** (`Auth/Registration/WebApp`) and run:

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

The username, email, and password fields and the **Create account** button have
all been read from the live page, so **the test is ready to run as-is**.

Two *optional* selectors in `pages/register_page.py` are still placeholders
(`SELECTOR_TBD_FROM_INSPECTOR`). You do **not** need them to run the test:

- `SUCCESS_MARKER` — fill in (from the page shown *after* registering) only if
  you want a stronger success check on top of "the form disappeared."
- `ERROR_MESSAGE` — fill in only if the app shows an error banner on a failed
  registration (e.g. "username already taken"), to make failure messages clearer.

### Changing the generated account
The username prefix, email domain, and password live in `credentials.json` under
`new_user`. Edit them there — never in the code.

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
2026-06-08 10:15:02 | INFO     | web_register | Logging initialized. Writing to logs/web_register_20260608_101502.log
2026-06-08 10:15:02 | INFO     | web_register | Starting Web Registration test against https://raspberrypi.peafowl-eagle.ts.net/furgechat/register
2026-06-08 10:15:02 | INFO     | web_register | Generated unique account -> username='qa_user_20260608_101502', email='qa_user_20260608_101502@example.com'
2026-06-08 10:15:05 | INFO     | web_register | Opened registration page; submitting the new-account form.
2026-06-08 10:15:07 | INFO     | web_register | REGISTRATION SUCCESSFUL for username 'qa_user_20260608_101502'.
2026-06-08 10:15:08 | INFO     | web_register | Browser closed.
```

- The generated username/email are logged so you can find the account later.
- A full log of every run is saved in the **`logs/`** folder.
- If the test fails, a screenshot is saved in the **`screenshots/`** folder with
  the time in its filename.
- The program's exit code is `0` on success and `1` on failure.

---

## 8. Troubleshooting — the 3 most likely failures

**1. The page never loads / `ERR_CONNECTION` / page-load timeout**
You are probably not on the network that can reach the private Tailscale
address. Connect to the correct VPN / Tailnet and confirm you can open
`https://raspberrypi.peafowl-eagle.ts.net/furgechat/register` manually in Chrome.

**2. "REGISTRATION FAILED — still on the register page"**
The app rejected the form. Most likely the email format or password did not meet
the app's rules, or (rarely) the generated username already exists. Open the
screenshot in `screenshots/` to see the exact on-screen message, and adjust the
`new_user` values in `credentials.json` if needed.

**3. It reports success but no account seems created (or vice-versa)**
Success is currently detected by the registration form disappearing. If the app
instead keeps the form on screen and shows an inline "Account created" message,
this check needs the post-registration element. Capture that element and add it
as `SUCCESS_MARKER` in `pages/register_page.py` for a precise check.

---

## 9. Files in this folder

| File | Purpose |
|------|---------|
| `main.py` | The test flow — what to do, in order. |
| `pages/register_page.py` | The registration screen's fields/button and actions. |
| `pages/base_page.py` | Shared browser actions (waits, typing, clicking). |
| `utils/data_generator.py` | Builds the unique username/email/password. |
| `utils/driver_factory.py` | Starts and configures Chrome. |
| `utils/config.py` | Reads settings from `credentials.json`. |
| `utils/logger.py` | Writes logs to the screen and to `logs/`. |
| `utils/screenshot.py` | Saves screenshots to `screenshots/` on failure. |
| `credentials.json` | The web address and new-account template. |
| `requirements.txt` | The Python packages to install. |
