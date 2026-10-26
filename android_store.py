import re
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from config.settings import settings
from pages.cart import CartContents


class AndroidStore:
    ACCOUNT = [
        (AppiumBy.ACCESSIBILITY_ID, "Account"),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)account")'),
    ]
    SIGN_IN = [
        (AppiumBy.ACCESSIBILITY_ID, "Sign In"),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)sign\\s*in")'),
    ]
    SEARCH = [
        (AppiumBy.ACCESSIBILITY_ID, "Search"),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Search")'),
    ]
    ADD_TO_CART = [
        (AppiumBy.ACCESSIBILITY_ID, "Add to Cart"),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)add to cart|add to bag")'),
    ]
    CART = [
        (AppiumBy.ACCESSIBILITY_ID, "Cart"),
        (AppiumBy.ACCESSIBILITY_ID, "Shopping Cart"),
        (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)cart")'),
    ]

    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.timeout = timeout or settings.timeout
        self.search_term = settings.search_term
        self.selected_product_name = ""

    def open_store(self):
        self._wait_any(self.SEARCH + self.ACCOUNT, "app home screen")

    def open_account_sign_in(self):
        self._wait_any(self.ACCOUNT, "Account tab").click()
        self._wait_any(self.SIGN_IN, "Sign In action").click()
        self._wait_any([(AppiumBy.CLASS_NAME, "android.widget.EditText")], "sign-in form")

    def submit_sign_in(self, email, password):
        fields = WebDriverWait(self.driver, self.timeout).until(
            lambda driver: (fields if len(fields := driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText")) >= 2 else False),
            message="Sign-in form should expose email and password fields",
        )
        fields[0].clear()
        fields[0].send_keys(email)
        fields[1].clear()
        fields[1].send_keys(password)
        try:
            self.driver.hide_keyboard()
        except Exception:
            pass
        self._wait_any(self.SIGN_IN, "Sign In submit button").click()

    def wait_for_signed_in_account(self):
        indicators = [
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("My Account")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Account Details")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("My Profile")'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textMatches("(?i)sign out|logout")'),
        ]
        try:
            element = self._wait_any(indicators, "signed-in account information")
            return (element.text or element.get_attribute("content-desc") or "").strip()
        except AssertionError as exc:
            errors = [
                element.text.strip()
                for element in self.driver.find_elements(AppiumBy.XPATH, "//*[@text]")
                if element.is_displayed() and any(word in element.text.casefold() for word in ("invalid", "incorrect", "failed"))
            ]
            raise AssertionError(
                f"Sign-in did not show account/profile information within {self.timeout}s. "
                f"Visible authentication errors: {errors[:3] or 'none detected'}."
            ) from exc

    def search_for(self, term):
        self.search_term = term
        self._wait_any(self.SEARCH, "search control").click()
        field = self._wait_any([(AppiumBy.CLASS_NAME, "android.widget.EditText")], "search input")
        field.clear()
        field.send_keys(term)
        self.driver.press_keycode(66)
        escaped_term = re.escape(term)
        self._wait_any(
            [(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textMatches("(?i).*{escaped_term}.*")'), *self.ADD_TO_CART],
            f"search results for {term!r}",
        )

    def open_first_product(self):
        result = self._wait_any(
            [(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().className("android.widget.TextView").textMatches("(?i).*{re.escape(self.search_term)}.*")')],
            "product search result",
        )
        result_name = (result.text or result.get_attribute("content-desc") or "").strip()
        result.click()
        self._wait_any(self.ADD_TO_CART, "product page Add to Cart button")
        title = self._visible_product_title()
        name = title or result_name
        if not name:
            raise AssertionError("Opened a product page, but could not read its name for cart verification.")
        self.selected_product_name = name
        return name

    def add_product_to_cart(self):
        self._wait_any(self.ADD_TO_CART, "Add to Cart button").click()

    def open_cart_and_read_contents(self):
        self._wait_any(self.CART, "cart control").click()
        self._wait_any(
            [(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Remove")'),
             (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Subtotal")')],
            "cart contents",
        )
        item_name = self._cart_item_name()
        return CartContents(item_name, self._read_quantity(), self._cart_badge_count())

    def _wait_any(self, locators, description):
        def find_visible(driver):
            for by, value in locators:
                for element in driver.find_elements(by, value):
                    if element.is_displayed() and element.is_enabled():
                        return element
            return False
        try:
            return WebDriverWait(self.driver, self.timeout).until(find_visible)
        except TimeoutException as exc:
            raise AssertionError(f"Timed out after {self.timeout}s waiting for {description}; locators tried: {locators}") from exc

    def _visible_product_title(self):
        for locator in [
            (AppiumBy.ACCESSIBILITY_ID, "Product Name"),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().resourceIdMatches(".*product.*(title|name).*")'),
        ]:
            for element in self.driver.find_elements(*locator):
                if element.is_displayed():
                    text = (element.text or element.get_attribute("content-desc") or "").strip()
                    if text:
                        return text
        return ""

    def _cart_item_name(self):
        # Read the visible cart text and look for the selected search term/product wording.
        for element in self.driver.find_elements(AppiumBy.XPATH, "//*[@text or @content-desc]"):
            value = (element.text or element.get_attribute("content-desc") or "").strip()
            if element.is_displayed() and value and self.selected_product_name.casefold() in value.casefold():
                return value
        return ""

    def _read_quantity(self):
        for element in self.driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.EditText"):
            value = (element.get_attribute("text") or element.get_attribute("value") or "").strip()
            if value.isdigit():
                return int(value)
        for element in self.driver.find_elements(AppiumBy.XPATH, "//*[@text]"):
            value = (element.get_attribute("text") or "").strip()
            if re.fullmatch(r"(?:Qty:?\s*)?\d+", value, re.I) and ("qty" in value.casefold() or value == "1"):
                return int(re.search(r"\d+", value).group())
        return None

    def _cart_badge_count(self):
        for element in self.driver.find_elements(AppiumBy.XPATH, "//*[@text or @content-desc]"):
            value = (element.text or element.get_attribute("content-desc") or "").strip()
            if element.is_displayed() and "cart" in value.casefold():
                match = re.search(r"\d+", value)
                if match:
                    return int(match.group())
        return None
