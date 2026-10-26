from pathlib import Path
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from appium import webdriver as appium_webdriver
from appium.options.android import UiAutomator2Options

from config.settings import settings
from pages.android_store import AndroidStore
from pages.web_store import WebStore


@pytest.fixture
def web_store():
    if settings.browser == "chrome":
        options = ChromeOptions()
        if settings.headless:
            options.add_argument("--headless=new")
        options.add_argument("--window-size=1440,1000")
        options.add_argument("--disable-notifications")
        driver = webdriver.Chrome(options=options)
    elif settings.browser == "firefox":
        options = FirefoxOptions()
        if settings.headless:
            options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Unsupported BROWSER={settings.browser!r}; choose chrome or firefox.")

    driver.set_page_load_timeout(45)
    try:
        yield WebStore(driver)
    finally:
        driver.quit()


@pytest.fixture
def android_store():
    settings.validate_android()
    capabilities = {
        "platformName": "Android",
        "appium:automationName": "UiAutomator2",
        "appium:deviceName": settings.android_device_name,
        "appium:noReset": False,
        "appium:newCommandTimeout": 120,
        "appium:autoGrantPermissions": True,
    }
    if settings.android_platform_version:
        capabilities["appium:platformVersion"] = settings.android_platform_version
    if settings.android_apk:
        capabilities["appium:app"] = str(Path(settings.android_apk).expanduser().resolve())
    else:
        capabilities["appium:appPackage"] = settings.android_package
        if settings.android_activity:
            capabilities["appium:appActivity"] = settings.android_activity

    options = UiAutomator2Options().load_capabilities(capabilities)
    driver = appium_webdriver.Remote(settings.appium_url, options=options)
    try:
        yield AndroidStore(driver)
    finally:
        driver.quit()
