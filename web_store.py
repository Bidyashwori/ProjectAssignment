import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from config.settings import settings
from pages.cart import CartContents
from utils.waits import any_visible, clickable


class WebStore:
    ACCOUNT = (By.CSS_SELECTOR, 'a[href*="account"], button[aria-label*="account" i]')
    SIGN_IN = (By.XPATH, "//*[self::a or self::button][contains(translate(normalize-space(.), 'SIGN IN', 'sign in'), 'sign in')]")
    EMAIL = (By.CSS_SELECTOR, 'input[type="email"], input[name*="email" i], input[autocomplete="email"]')
    PASSWORD = (By.CSS_SELECTOR, 'input[type="password"]')
    SIGN_IN_SUBMIT = (By.XPATH, "//button[@type='submit' or contains(translate(normalize-space(.), 'SIGN IN', 'sign in'), 'sign in')]")
    SEARCH = (By.CSS_SELECTOR, 'input[type="search"], input[name*="search" i], input[placeholder*="search" i]')
    PRODUCT_LINK = (By.CSS_SELECTOR, 'a[href*="/p/"], a[href*="/product/"]')
    ADD_TO_CART = (By.XPATH, "//button[contains(translate(normalize-space(.), 'ADD TO CART', 'add to cart'), 'add to cart') or contains(translate(normalize-space(.), 'ADD TO BAG', 'add to bag'), 'add to bag')]")
    CART = (By.CSS_SELECTOR, 'a[href*="cart" i], button[aria-label*="cart" i]')

    def __init__(self, driver, timeout=None):
        self.driver = driver
        self.timeout = timeout or settings.timeout

    def open_store(self):
        self.driver.get(settings.base_url)
        any_visible(self.driver, [self.SEARCH, self.ACCOUNT], self.timeout, "store search or account control")

    def open_account_sign_in(self):
        if not self._is_visible(self.SIGN_IN):
            clickable(self.driver, self.ACCOUNT, self.timeout).click()
        clickable(self.driver, self.SIGN_IN, self.timeout).click()
        any_visible(self.driver, [self.EMAIL], self.timeout, "sign-in email field")

    def submit_sign_in(self, email, password):
        email_field = any_visible(self.driver, [self.EMAIL], self.timeout, "email field")
        password_field = any_visible(self.driver, [self.PASSWORD], self.timeout, "password field")
        email_field.clear()
        email_field.send_keys(email)
        password_field.clear()
        password_field.send_keys(password)
        clickable(self.driver, self.SIGN_IN_SUBMIT, self.timeout).click()

    def wait_for_signed_in_account(self):
        account_indicators = [
            (By.CSS_SELECTOR, '[data-testid*="account-details" i], [data-testid*="profile" i]'),
            (By.XPATH, "//*[self::h1 or self::h2 or self::h3][contains(translate(normalize-space(.), 'MY ACCOUNT', 'my account'), 'my account') or contains(translate(normalize-space(.), 'PROFILE', 'profile'), 'profile') or contains(translate(normalize-space(.), 'ACCOUNT DETAILS', 'account details'), 'account details')]"),
            (By.XPATH, "//*[self::a or self::button][contains(translate(normalize-space(.), 'SIGN OUT', 'sign out'), 'sign out') or contains(translate(normalize-space(.), 'LOGOUT', 'logout'), 'logout')]")
        ]
        try:
            element = any_visible(self.driver, account_indicators, self.timeout, "signed-in account information")
            return (element.text or element.get_attribute("aria-label") or "").strip()
        except TimeoutException as exc:
            raise AssertionError(
                f"Sign-in did not show account/profile information within {self.timeout}s; "
                f"current URL is {self.driver.current_url!r}. Check credentials or the current sign-in UI."
            ) from exc

    def search_for(self, term):
        field = any_visible(self.driver, [self.SEARCH], self.timeout, "product search field")
        field.clear()
        field.send_keys(term)
        field.submit()
        any_visible(self.driver, [self.PRODUCT_LINK], self.timeout, f"search results for {term!r}")

    def open_first_product(self):
        product = any_visible(self.driver, [self.PRODUCT_LINK], self.timeout, "first product result")
        product.click()
        title = any_visible(self.driver, [(By.CSS_SELECTOR, "h1")], self.timeout, "product page title")
        name = title.text.strip()
        if not name:
            raise AssertionError("Product page opened, but its h1 title was empty; cannot verify the cart item.")
        any_visible(self.driver, [self.ADD_TO_CART], self.timeout, "Add to Cart button")
        return name

    def add_product_to_cart(self):
        clickable(self.driver, self.ADD_TO_CART, self.timeout).click()

    def open_cart_and_read_contents(self):
        clickable(self.driver, self.CART, self.timeout).click()
        line_item = any_visible(
            self.driver,
            [(By.CSS_SELECTOR, '[data-testid*="cart-item" i], [class*="cart-item" i], [class*="cartItem" i]')],
            self.timeout,
            "cart line item",
        )
        name_element = self._find_name(line_item)
        item_name = (name_element.text if name_element else line_item.text.split("\n")[0]).strip()
        quantity = self._read_quantity(line_item)
        return CartContents(item_name, quantity, self._cart_badge_count())

    def _is_visible(self, locator):
        return any(element.is_displayed() for element in self.driver.find_elements(*locator))

    @staticmethod
    def _find_name(container):
        for locator in [(By.CSS_SELECTOR, "a"), (By.CSS_SELECTOR, "h2"), (By.CSS_SELECTOR, "h3")]:
            try:
                element = container.find_element(*locator)
                if element.text.strip():
                    return element
            except NoSuchElementException:
                continue
        return None

    @staticmethod
    def _read_quantity(container):
        selectors = [
            (By.CSS_SELECTOR, 'input[type="number"]'),
            (By.CSS_SELECTOR, 'input[aria-label*="quantity" i]'),
            (By.CSS_SELECTOR, '[data-testid*="quantity" i]'),
            (By.CSS_SELECTOR, 'select[name*="quantity" i]'),
        ]
        for locator in selectors:
            for element in container.find_elements(*locator):
                value = (element.get_attribute("value") or element.text or "").strip()
                if value.isdigit():
                    return int(value)
        text = container.text or ""
        match = re.search(r"(?:qty|quantity)\s*[:x]?\s*(\d+)", text, re.I)
        return int(match.group(1)) if match else None

    def _cart_badge_count(self):
        for locator in [
            (By.CSS_SELECTOR, '[data-testid*="cart-count" i], [class*="cart-count" i]'),
            (By.CSS_SELECTOR, '[aria-label*="cart" i][aria-label*="item" i]'),
        ]:
            for element in self.driver.find_elements(*locator):
                if element.is_displayed():
                    match = re.search(r"\d+", (element.text or element.get_attribute("aria-label") or ""))
                    if match:
                        return int(match.group())
        return None
