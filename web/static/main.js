// static/main.js

console.log("Sanity check!");
console.log(document.getElementById('ciao'));
console.log(document.querySelector("subscription-form"))

var stripe = Stripe('pk_test_51Hr7tlCPJO2Tjuq1PUy2FdjQAvuDkRPNxYWvN2YwdOWqykdtKBZArXrFRXjZ4R7IkcAwDmAbwnd57M5gPplJIjej00BrnpqbdI');

stripeElements();
document.querySelector("#spinner").classList.add("hidden");

function stripeElements() {
    if (document.getElementById('card-element')) {
        let elements = stripe.elements();

        // Card Element styles
        let style = {
            base: {
                color: "#32325d",
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                fontSmoothing: "antialiased",
                fontSize: "16px",
                "::placeholder": {
                    color: "#aab7c4"
                }
            },
            invalid: {
                color: "#fa755a",
                iconColor: "#fa755a"
            }
        };

        if (window.has_payment_method === 'False') {


            var card = elements.create('card', {style: style});

            card.mount('#card-element');

            card.on('focus', function () {
                let el = document.getElementById('card-errors');
                el.classList.add('focused');
            });

            card.on('blur', function () {
                let el = document.getElementById('card-errors');
                el.classList.remove('focused');
            });

            card.on('change', function (event) {
                displayError(event);
            });
        }
    }
    //we'll add payment form handling here
        console.log('payment method')
        let paymentForm = document.getElementById('subscription-form');
        console.log(paymentForm)
        console.log(document.getElementById("submitCheckout"))
        document.getElementById("submitCheckout").disabled = true;
        var selectedPlanId = null;
        if (paymentForm) {

            paymentForm.addEventListener('submit', function (evt) {
                evt.preventDefault();
                changeLoadingState(true);

                if (window.has_payment_method === 'False') {
                    // create new payment method & create subscription
                    createPaymentMethod({card});
                } else {
                    subscribe({card})
                }

            });
        }
}

function createPaymentMethod({card}) {

    // Set up payment method for recurring usage
    let billingName = '{{user.username}}';
    stripe
        .createPaymentMethod({
            type: 'card',
            card: card,
            billing_details: {
                name: billingName,
            },
        })
        .then((result) => {
            if (result.error) {
                displayError(result);
            } else {
                const paymentParams = {
                    price_id: document.getElementById("priceId").innerHTML,
                    payment_method: result.paymentMethod.id,
                    card: card
                };
                fetch("/api/frontend/payments/create-sub", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token }}',
                    },
                    credentials: 'same-origin',
                    body: JSON.stringify(paymentParams),
                }).then((response) => {
                    return response.json();
                }).then((result) => {
                    if (result.error) {
                        // The card had an error when trying to attach it to a customer
                        throw result;
                    }
                    return result;
                }).then((result) => {
                    if (result && result.status === 'active') {

                        window.location.href = '/api/frontend/payments/charge/complete';
                    }
                    ;
                }).catch(function (error) {
                    displayError(result.error.message);

                });
            }
        });
}

function subscribe({card}) {
    const paymentParams = {
        price_id: document.getElementById("priceId").innerHTML,
        payment_method: null,
        card: card
    };
    fetch("/api/frontend/payments/create-sub", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}',
        },
        credentials: 'same-origin',
        body: JSON.stringify(paymentParams),
    }).then((response) => {
        return response.json();
    }).then((result) => {
        if (result.error) {
            // The card had an error when trying to attach it to a customer
            throw result;
        }
        return result;
    }).then((result) => {
        if (result && result.status === 'active') {

            window.location.href = '/api/frontend/payments/charge/complete';
        }
        ;
    }).catch(function (error) {
        displayError(result.error.message);

    });
}



var changeLoadingState = function (isLoading) {
    if (isLoading) {
        document.getElementById("submitCheckout").disabled = true;
        document.querySelector("#spinner").classList.remove("hidden");
        document.querySelector("#button-text").classList.add("hidden");
    } else {
        document.getElementById("submitCheckout").disabled = false;
        document.querySelector("#spinner").classList.add("hidden");
        document.querySelector("#button-text").classList.remove("hidden");
    }
};

function displayError(event) {

    let displayError = document.getElementById('card-errors');
    if (event.error) {
        displayError.textContent = event.error.message;
    } else {
        displayError.textContent = '';
    }
}

function planSelect(name, price, priceId) {
    var inputs = document.getElementsByTagName('input');

    for (var i = 0; i < inputs.length; i++) {
        inputs[i].checked = false;
        if (inputs[i].name == name) {

            inputs[i].checked = true;
        }
    }

    selectedPlanId = priceId;
    var n = document.getElementById('plan');
    var p = document.getElementById('price');
    var pid = document.getElementById('priceId');
    console.log(priceId)
    console.log(name)
    n.innerHTML = name;
    p.innerHTML = price;
    pid.innerHTML = priceId;
    document.getElementById("submitCheckout").disabled = false;


}


// Get Stripe publishable key
fetch("/api/frontend/payments/config/")
    .then((result) => {
        return result.json();
    })
    .then((data) => {
        // Initialize Stripe.js
        const stripe = Stripe(data.publicKey);

        // new
        // Event handler
        document.querySelector("#submitBtn").addEventListener("click", () => {
            // Get Checkout Session ID
            fetch("/api/frontend/payments/create-checkout-session/?plan_id=" + selectedPlanId)
                .then((result) => {
                    return result.json();
                })
                .then((data) => {
                    console.log(data);
                    // Redirect to Stripe Checkout
                    return stripe.redirectToCheckout({sessionId: data.sessionId})
                })
                .then((res) => {
                    console.log(res);
                });
        });
    });