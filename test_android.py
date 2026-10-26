import pytest

from config.settings import settings
from workflows import successful_add_to_cart, successful_sign_in


@pytest.mark.app
@pytest.mark.signin
def test_android_successful_sign_in(android_store):
    settings.require_credentials()
    successful_sign_in(android_store, settings.email, settings.password)


@pytest.mark.app
@pytest.mark.cart
def test_android_successful_add_to_cart(android_store):
    successful_add_to_cart(android_store, settings.search_term)
