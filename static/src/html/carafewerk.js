   // JavaScript code to toggle the cart and overlay
   document.getElementById('cartButton').addEventListener('click', function () {
    toggleCart();
  });

  document.getElementById('closeCartButton').addEventListener('click', function () {
    toggleCart();
  });

  // Function to toggle cart and overlay
  function toggleCart() {
    var cart = document.getElementById('cart');
    var cartButton = document.getElementById('cartButton');
    var overlay = document.getElementById('body_id');

    if (cart.classList.contains('open')) {
      cart.classList.remove('open');
      cartButton.style.right = '20px';
      overlay.classList.remove('overly');
    } else {
      overlay.classList.add('overly');
      cart.classList.add('open');
      cartButton.style.right = '340px'; // Adjust this value to match the width of the cart plus some margin
    }
  }

  // Close cart if clicking outside of it
  document.addEventListener('click', function (event) {
    var overlay = document.getElementById('body_id');
    var isClickInsideCart = cart.contains(event.target);
    var isClickInsideCartButton = event.target === cartButton;
    if (!isClickInsideCart && !isClickInsideCartButton) {
      cart.classList.remove('open');
      cartButton.style.right = '20px';
      overlay.classList.remove('overly');
    }
  });