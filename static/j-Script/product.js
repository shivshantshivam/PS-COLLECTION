const cartButtons = document.querySelectorAll(".add-to-cart-button");

cartButtons.forEach(button => {

    button.addEventListener("click", function () {

        const productId = this.dataset.cartProductId;

        fetch("/add-to-cart", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: "product_id=" + productId
        })
        .then(response => response.text())
        .then(data => {

            console.log(data);

            alert("Product added to cart!");

        })
        .catch(error => {

            console.log(error);

            alert("Something went wrong.");

        });

    });

});


const wishlistButtons = document.querySelectorAll(".wishlist-heart");

wishlistButtons.forEach(button => {

    button.addEventListener("click", function () {

        const productId = this.dataset.wishlistId;

        const confirmAdd = confirm(
            "Do you want to add this product to your wishlist?"
        );

        if (confirmAdd) {

            window.location.href =
                "/add-to-wishlist/" + productId;

        }

    });

});


function toggleDescription(button) {

    const description = button.previousElementSibling;

    description.classList.toggle("show-full");

    if (description.classList.contains("show-full")) {

        button.textContent = "See Less";

    } else {

        button.textContent = "See More";

    }

}