# Web New Chat — Automated Test Guide

This folder contains an automated test that opens the **Furgechat web app**, signs
in, goes to the **"New Chat"** tab, starts a chat with a chosen user, and sends a
first message. If anything goes wrong it takes a screenshot, writes a log file,
and reports a failure.

You do **not** need to be a programmer to run it — just follow the steps below.

---

## 1. What this test does (in plain English)

1. Opens Chrome and signs in with the `admin` / `password` account.
2. Goes to the Furgechat **New Chat** tab.
3. Types the recipient's username and the first message.
4. Clicks **Create Chat**.
5. Confirms it worked by checking that the New Chat form goes away.
6. Prints **NEW CHAT CREATED** and stops — or, if it failed, prints a clear
   error, saves a screenshot, and stops with an error.

---

## 2. Acceptance criteria (from the assessment PDF)

> **New Chat:** Start a new chat with a user, send the message
> "Hey user! This is done for assessment".

This test satisfies that requirement by opening the New Chat form, entering a
recipient and that exact message, and submitting it.

---

## 3. A note on this page's "known quirks"

The New Chat page deliberately contains a quirk: the **Recipient box has an ID
that changes every time the page loads** (for example `recipient-ejgdyfp`). A
test that relied on that ID would break immediately.

This test handles it by finding the Recipient box using its stable **name**
(`recipient`) instead of its changing ID — so it keeps working no matter what
the ID happens to be. No changes to the website are needed or recommended.

---

## 4. Prerequisites

Before you run the test you need:

- **Python 3.11 or newer** installed. Check with `python --version`.
- **Google Chrome** installed (any recent version). The test downloads the
  matching browser driver automatically — you do not install that yourself.
- **Network access** to the Furgechat address
  (`https://raspberrypi.peafowl-eagle.ts.net/...`). This is a private Tailscale
  address, so you must be on the correct VPN / Tailnet to reach it. Confirm by
  opening the address in Chrome manually first.

---

## 5. Setup (one time)

Open a terminal **in this folder** (`Chat/NewChat/WebApp`) and run:

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

## 6. Settings you can change (no code editing)

Everything is in `credentials.json`:

- `new_chat.recipient` — who to start the chat with. Defaults to `Alice` (a user
  already seen in the Chats tab). **Change this to the username you intend.**
- `new_chat.message` — the first message. Defaults to the exact assessment text.
- `login.enabled` — `true` by default, because creating a chat requires signing
  in. Set to `false` only if your environment does not require a login.

The page selectors are already filled in (see the quirk note in step 3), so
there is nothing in the code to edit.

---

## 7. How to run

With the virtual environment active (step 5):

```bash
python main.py
```

---

## 8. What to expect

A successful run prints something like:

```
2026-06-08 10:15:02 | INFO     | web_new_chat | Logging initialized. Writing to logs/web_new_chat_20260608_101502.log
2026-06-08 10:15:02 | INFO     | web_new_chat | Starting Web New Chat test against https://raspberrypi.peafowl-eagle.ts.net/furgechat/new-chat
2026-06-08 10:15:03 | INFO     | web_new_chat | Signing in as 'admin' before creating a chat.
2026-06-08 10:15:06 | INFO     | web_new_chat | Login successful.
2026-06-08 10:15:07 | INFO     | web_new_chat | Opened the 'New Chat' tab.
2026-06-08 10:15:07 | INFO     | web_new_chat | Creating a new chat with recipient 'Alice'.
2026-06-08 10:15:07 | INFO     | web_new_chat | First message: 'Hey user! This is done for assessment'
2026-06-08 10:15:09 | INFO     | web_new_chat | NEW CHAT CREATED with 'Alice'; first message sent.
2026-06-08 10:15:10 | INFO     | web_new_chat | Browser closed.
```

- A full log of every run is saved in the **`logs/`** folder.
- If the test fails, a screenshot is saved in the **`screenshots/`** folder with
  the time in its filename.
- The program's exit code is `0` on success and `1` on failure.

---

## 9. Troubleshooting — the 3 most likely failures

**1. Login fails / "The New Chat form did not load"**
The test could not sign in, so it never reached the New Chat form. Confirm the
`login` credentials in `credentials.json` are correct and that you can log in
manually. The login button only enables after the "I am not a robot" box is
ticked — the test does this automatically, but a very slow page may need a higher
`timeouts.explicit_wait_seconds`.

**2. "NEW CHAT FAILED — still on the New Chat page"**
The form was submitted but the app stayed put. The recipient is probably not a
valid/known username. Open `credentials.json` and set `new_chat.recipient` to a
real user, then check the screenshot in `screenshots/` for the on-screen message.

**3. The page never loads / `ERR_CONNECTION` / page-load timeout**
You are probably not on the network that can reach the private Tailscale
address. Connect to the correct VPN / Tailnet and confirm you can open
`https://raspberrypi.peafowl-eagle.ts.net/furgechat/new-chat` manually in Chrome.

---

## 10. Files in this folder

| File | Purpose |
|------|---------|
| `main.py` | The test flow — what to do, in order. |
| `pages/new_chat_page.py` | The New Chat form: fields, the quirk handling, submit. |
| `pages/login_page.py` | The sign-in step that runs before creating the chat. |
| `pages/base_page.py` | Shared browser actions (waits, typing, clicking). |
| `utils/driver_factory.py` | Starts and configures Chrome. |
| `utils/config.py` | Reads settings from `credentials.json`. |
| `utils/logger.py` | Writes logs to the screen and to `logs/`. |
| `utils/screenshot.py` | Saves screenshots to `screenshots/` on failure. |
| `credentials.json` | The web address, recipient/message, and login details. |
| `requirements.txt` | The Python packages to install. |
