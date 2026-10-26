from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def visible(driver, locator, timeout):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))


def clickable(driver, locator, timeout):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def any_visible(driver, locators, timeout, description):
    def find_visible(browser):
        for locator in locators:
            for element in browser.find_elements(*locator):
                if element.is_displayed():
                    return element
        return False

    return WebDriverWait(driver, timeout).until(
        find_visible,
        message=f"Timed out after {timeout}s waiting for {description}. Tried: {locators}",
    )
