function showSccuessMessage() {
    $(".cart-update-msg").removeClass("hidden");
    // hideSccuessMessage().delay(2000);
    // setTimeout( hideSccuessMessage(), 2000 );
}

function hideSccuessMessage() {
    $(".cart-update-msg").addClass("hidden");
}

function updateCart(productId, action) {
    if (user == "AnonymousUser") {
        addCookieItem(productId, action);
    } else {
        updateUserCart(productId, action);
    }
}

function addCookieItem(productId, action) {
    if (action == "add") {
        if (cart[productId] == undefined) {
            cart[productId] = { quantity: 1 };
        } else {
            cart[productId]["quantity"] += 1;
        }
    }

    if (action == "remove") {
        cart[productId]["quantity"] -= 1;

        if (cart[productId]["quantity"] <= 0) {
            delete cart[productId];
        }
    }

    document.cookie = "cart=" + JSON.stringify(cart);
}

function removeCartItem(productId) {
    var url = "/remove_item/";
    $.ajax({
        method: "POST",
        url: url,
        type: "application/json",
        headers: { "X-CSRFToken": csrftoken },
        data: {
            productId: productId,
        },
        success: function(data) {
            window.location.reload(true);
            // showSccuessMessage();
        },
    });
}

function updateUserCart(productId, action) {
    var url = "/update_item/";
    $.ajax({
        method: "POST",
        url: url,
        type: "application/json",
        headers: { "X-CSRFToken": csrftoken },
        data: {
            productId: productId,
            action: action,
        },
        success: function(data) {
            window.location.reload(true);
            // showSccuessMessage();
        },
    });
}