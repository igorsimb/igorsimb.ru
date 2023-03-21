var updateBtns = document.getElementsByClassName('update-cart')
var removeItem = document.getElementById('remove-item')


// removeItem.addEventListener('click', function() {
//     var productId = this.dataset.product
//     var action = this.dataset.action
//
//     console.log('Removing', productId)
//     if (user == 'AnonymousUser') {
//         addCookieItem(productId, action='remove')
//     } else {
//         updateUserOrder(productId, action='remove')
//     }
// })

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('productId:', productId, 'Action', action)

        console.log('USER:', user)
        if (user === 'AnonymousUser') {
            addCookieItem(productId, action)
        } else {
            updateUserOrder(productId, action)
        }
    })
}

// Controls item quantities when user is NOT logged in
function addCookieItem(productId, action) {
    console.log('Not logged in...')

    if (action === 'add') {
        // if no items in cart, we create 1, if there are items, we add
        if (cart[productId] === undefined) {
            cart[productId] = {'quantity': 1}
        } else {
            cart[productId]['quantity'] += 1
        }
    }

    if (action === 'remove') {
        cart[productId]['quantity'] -= 1

        if (cart[productId]['quantity'] <= 0) {
            console.log('Remove Item')
            delete cart[productId]
        }
    }
    if (action === 'delete') {
        delete cart[productId]
        console.log(productId, 'deleted')
    }
    console.log('Cart:', cart)
    document.cookie = 'cart=' + JSON.stringify(cart) + ';domain=;path=/'
    location.reload()
}

/* This is what the anonymous cart looks like:
    cart = {
        1:{'quantity':4},
        4:{'quantity':1},
        6:{'quantity':2},
*/


function updateUserOrder(productId, action) {
    console.log('User is authenticated, sending data...')

    var url = '/update_item/'

    // fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({'productId': productId, 'action': action})
    })
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log('Data:', data)
            location.reload()
        });
}







