# Web Chats — Automated Test Guide

This folder contains an automated test that opens the **Furgechat web app**, goes
to the **"Chats"** tab, and prints every chat shown there — the contact/group
name and the last-message preview. If anything goes wrong it takes a screenshot,
writes a log file, and reports a failure.

You do **not** need to be a programmer to run it — just follow the steps below.

---

## 1. What this test does (in plain English)

1. Opens Chrome and (optionally) logs in — see step 5.
2. Goes to the Furgechat **Chats** tab.
3. Reads every chat in the list.
4. Prints each chat's number, name, and last message to the screen and to a log
   file.
5. Prints the total count and stops — or, if it failed, prints a clear error,
   saves a screenshot, and stops with an error.

---

## 2. Acceptance criteria (from the assessment PDF)

> **Chats:** Develop a script to print all the visible chats under the "Chats"
> tab.

This test satisfies that requirement by reading every chat row on the Chats tab
and printing its name and last-message preview.

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

Open a terminal **in this folder** (`Chat/Chats/WebApp`) and run:

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

## 5. Do you need to log in first?

This test tries to open the Chats tab **directly**. That is the simplest path and
needs no setup.

**If the app sends you to the login page instead of showing your chats**, open
`credentials.json` and change `login.enabled` from `false` to `true`. The test
will then log in with the `admin` / `password` credentials (already in the file)
before reading the chats. No code changes are needed.

The selectors for the chats list are already filled in from the live page, so
there is nothing else to edit.

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
2026-06-08 10:15:02 | INFO     | web_chats | Logging initialized. Writing to logs/web_chats_20260608_101502.log
2026-06-08 10:15:02 | INFO     | web_chats | Starting Web Chats test against https://raspberrypi.peafowl-eagle.ts.net/furgechat/chats
2026-06-08 10:15:05 | INFO     | web_chats | Opened the 'Chats' tab.
2026-06-08 10:15:06 | INFO     | web_chats | Found 3 chat(s) under the 'Chats' tab:
2026-06-08 10:15:06 | INFO     | web_chats |   [1] Alice — "See you tomorrow!"
2026-06-08 10:15:06 | INFO     | web_chats |   [2] Bob — "Thanks for the file."
2026-06-08 10:15:06 | INFO     | web_chats |   [3] Team QA — "Sprint planning at 10am."
2026-06-08 10:15:07 | INFO     | web_chats | Browser closed.
```

- A full log of every run is saved in the **`logs/`** folder.
- If the test fails, a screenshot is saved in the **`screenshots/`** folder with
  the time in its filename.
- The program's exit code is `0` on success and `1` on failure.

---

## 8. Troubleshooting — the 3 most likely failures

**1. "The chats list did not load" / you see the login page**
The Chats tab needs you to be signed in. Open `credentials.json` and set
`login.enabled` to `true`, then run again (see step 5).

**2. The page never loads / `ERR_CONNECTION` / page-load timeout**
You are probably not on the network that can reach the private Tailscale
address. Connect to the correct VPN / Tailnet and confirm you can open
`https://raspberrypi.peafowl-eagle.ts.net/furgechat/chats` manually in Chrome.

**3. "No chats are currently visible under the 'Chats' tab"**
The screen loaded but found no chats. Either the signed-in account genuinely has
no chats, or you are signed in as a different user than expected. Check the
screenshot/log, and confirm the `login.username` in `credentials.json` is the
account whose chats you expect to see.

---

## 9. Files in this folder

| File | Purpose |
|------|---------|
| `main.py` | The test flow — what to do, in order. |
| `pages/chat_list_page.py` | The Chats tab: how to find and read each chat. |
| `pages/login_page.py` | Optional sign-in step (used only if enabled). |
| `pages/base_page.py` | Shared browser actions (waits, typing, clicking). |
| `utils/driver_factory.py` | Starts and configures Chrome. |
| `utils/config.py` | Reads settings from `credentials.json`. |
| `utils/logger.py` | Writes logs (and the chat list) to screen and `logs/`. |
| `utils/screenshot.py` | Saves screenshots to `screenshots/` on failure. |
| `credentials.json` | The web address and the optional login details. |
| `requirements.txt` | The Python packages to install. |
