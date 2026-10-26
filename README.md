# Mumzworld Automation Tests

Python automation for the four required Mumzworld journeys:

* **A1:** Website sign-in
* **A2:** Website add to cart
* **B1:** Android sign-in
* **B2:** Android add to cart

Tests stop at the cart. No checkout or order is performed.

## Tech stack

Python, pytest, Selenium for web, and Appium with UiAutomator2 for Android. Page objects keep UI locators separate from tests, while `workflows.py` shares sign-in and cart assertions between platforms.

## Setup

Requires Python 3.10+, a browser for web tests, and a dedicated Mumzworld test account. Android tests also require Android SDK, an emulator/device, Appium 2, UiAutomator2, and the Mumzworld app.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

## Run website tests

```bash
pytest -m web -v
```

## Run Android tests

Start an emulator/device and Appium, then run:

```bash
appium driver install uiautomator2
appium
pytest -m app -v
```

Configure the Android app details in `.env` before running.

## Verification

Sign-in checks that account information is visible. Add-to-cart checks that the selected product appears in the cart and that its quantity is `1`; if a readable quantity is not available, the test fails rather than guessing. A numeric cart badge is checked when available.



```bash
pytest -m web -v
pytest -m web -v
pytest -m app -v
pytest -m app -v
```



