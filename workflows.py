def successful_sign_in(store, email, password):
    store.open_store()
    store.open_account_sign_in()
    store.submit_sign_in(email, password)
    account = store.wait_for_signed_in_account()
    assert account.strip(), "Expected visible account/profile information after sign-in, but none was found."


def successful_add_to_cart(store, search_term):
    store.open_store()
    store.search_for(search_term)
    selected_name = store.open_first_product()
    assert selected_name.strip(), "The selected product had no readable name; cart verification would be unreliable."

    store.add_product_to_cart()
    cart = store.open_cart_and_read_contents()

    assert cart.item_name.strip(), "The cart opened, but no product name was found in its line item."
    selected = _normalise(selected_name)
    actual = _normalise(cart.item_name)
    assert selected in actual or actual in selected, (
        f"Wrong product in cart: selected {selected_name!r}, but cart showed {cart.item_name!r}."
    )
    assert cart.quantity is not None, (
        f"Could not read the quantity for {cart.item_name!r}; expected the cart UI to expose quantity 1."
    )
    assert cart.quantity == 1, (
        f"Wrong quantity for {cart.item_name!r}: expected 1 after one Add to Cart action, got {cart.quantity}."
    )
    if cart.badge_count is not None:
        assert cart.badge_count >= 1, (
            f"Cart badge should show at least one item after adding {selected_name!r}, got {cart.badge_count}."
        )


def _normalise(value):
    return " ".join(value.casefold().split())
