# Buzzerfan — QA Automation Assessment

Automated UI tests for the **Furgechat** chat application across **Web** (Selenium)
and **Android** (Appium + UiAutomator2), written in **Python 3.11+**.

There are **8 self-contained test scripts** — 4 features × 2 platforms — each in
its own folder following `Module/Feature/Platform/`. Every folder runs on its own
and ships a non-technical `Guide.MD`.

---

## Features

| Module | Feature | Web (Selenium) | Android (Appium) | What it does |
|--------|---------|----------------|------------------|--------------|
| Auth | Login | [Auth/Login/WebApp](Auth/Login/WebApp) | [Auth/Login/Android](Auth/Login/Android) | Log into a user account and verify success. |
| Auth | Registration | [Auth/Registration/WebApp](Auth/Registration/WebApp) | [Auth/Registration/Android](Auth/Registration/Android) | Create a new account (unique, timestamp-based). |
| Chat | Chats | [Chat/Chats/WebApp](Chat/Chats/WebApp) | [Chat/Chats/Android](Chat/Chats/Android) | Print all visible chats on the dashboard. |
| Chat | New Chat | [Chat/NewChat/WebApp](Chat/NewChat/WebApp) | [Chat/NewChat/Android](Chat/NewChat/Android) | Start a new chat and send message(s). |

Each feature's own **`Guide.MD`** has the full, non-technical prerequisites,
setup, run, expected-output, and troubleshooting instructions.

---

## Folder layout

Every feature folder is self-contained:

```
<Module>/<Feature>/<Platform>/
├── Guide.MD              # plain-English run guide
├── main.py              # the test flow (orchestration only)
├── requirements.txt     # Python dependencies
├── credentials.json     # URLs / capabilities / login details (no hardcoding)
├── pages/               # Page Object Model: locators + actions
│   ├── base_page.py     # shared waits / typing / clicking
│   └── <screen>_page.py # one class per screen
└── utils/               # logger, driver factory, (config/test-data helpers)
```

`logs/` and `screenshots/` are created at runtime and are git-ignored.

---

## Conventions (applied across all 8)

- **Page Object Model** — locators and actions live in `pages/`; `main.py` only
  orchestrates the flow and never contains raw locators.
- **Explicit waits only** — every wait is a `WebDriverWait` + `expected_conditions`
  on a real DOM/UI condition. **No `time.sleep` is used as a wait** anywhere.
- **Locator priority** — Web: `data-testid` > `id` > `name` > CSS > (relative) XPath.
  Android: accessibility id (content-desc) > resource-id > UiAutomator > XPath.
  Where the preferred locators don't exist (e.g. Flutter EditTexts with no
  id/content-desc), the fallback is documented in the page object.
- **No hardcoding** — URLs, capabilities, and credentials come from
  `credentials.json` (and `capabilities.json` on Android).
- **Failure contract** — on any failure the script logs a clear message, saves a
  timestamped screenshot to `screenshots/`, and exits non-zero. The driver is
  always released in a `finally` block.
- **Logging** — all output goes through a logger (`utils/logger.py`) to both
  stdout and a timestamped file under `logs/` (no bare `print()`).

---

## Prerequisites

**Web features** (`*/WebApp/`):
- Python 3.11+
- Google Chrome (the matching driver is downloaded automatically by Selenium Manager)
- Network access to the Furgechat URL (a private Tailscale address — VPN/Tailnet required)

**Android features** (`*/Android/`):
- Python 3.11+, JDK 17, Android SDK (`ANDROID_HOME` set, `adb` on PATH)
- Node.js + Appium 2 server on `:4723` with the `uiautomator2` driver
  (`npm i -g appium` → `appium driver install uiautomator2` → `appium`)
- A running emulator (`emulator-5554`, Pixel 10 Pro, Android 13)
- **The app file at `Assets/furgechat.apk`** (repo root) — see below

---

## Running a feature

Open a terminal **in the feature's folder** and follow its `Guide.MD`. The
general shape:

```bash
# from <Module>/<Feature>/<Platform>/
python -m venv venv
# Windows:  .\venv\Scripts\Activate.ps1     macOS/Linux:  source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Exit code `0` = pass, `1` = fail (with a screenshot in `screenshots/` and a log in `logs/`).

---

## The Android APK

The 4 Android features launch the app from **`Assets/furgechat.apk`** (relative
to this repo root). The path is read from each feature's `credentials.json`
(`apk_path`) and resolved to an absolute path at runtime, so it is portable.
**Place `furgechat.apk` into an `Assets/` folder at the repo root before running
the Android tests** (or set `apk_path` to an absolute path).

---

## Credentials handling

- **Web features** commit `credentials.json` (it is a required deliverable and
  holds only the assessment's public test values, e.g. `admin` / `password`).
- **Android features** keep the real `credentials.json` **git-ignored** and commit
  a `credentials.example.json` template instead. Copy it before running:
  ```bash
  cp credentials.example.json credentials.json   # then fill in the values
  ```

---

## Tech stack

Selenium (Web) · Appium-Python-Client + UiAutomator2 (Android) · Python 3.11+ ·
Page Object Model. Web uses Selenium Manager (no manual driver); Android requires
a running Appium 2 server and emulator.
