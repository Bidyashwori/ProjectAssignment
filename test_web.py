import pytest

from config.settings import settings
from workflows import successful_add_to_cart, successful_sign_in


@pytest.mark.web
@pytest.mark.signin
def test_web_successful_sign_in(web_store):
    settings.require_credentials()
    successful_sign_in(web_store, settings.email, settings.password)


@pytest.mark.web
@pytest.mark.cart
def test_web_successful_add_to_cart(web_store):
    successful_add_to_cart(web_store, settings.search_term)
