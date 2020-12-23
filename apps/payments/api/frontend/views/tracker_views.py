import json

import djstripe
import stripe
from celery.utils.serialization import jsonify
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from djstripe.models import Product

from apps.profile.models import Profile
from web.settings import STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY

def home(request):
    has_payment_method = False
    customer_id = request.GET.get('customer_id')
    prod_list = []
    # products = Product.objects.all()
    # print('number of plans stripe: ')
    # print(len(products))
    products = Product.objects.filter(name__in=['Trial', 'Standard', 'Premium'])
    for product in products:
        if product.name == 'Trial':
            prod_list.append(product)
    for product in products:
        if product.name == 'Standard':
            prod_list.append(product)
    for product in products:
        if product.name == 'Premium':
            prod_list.append(product)
    if customer_id:
        customer = stripe.Customer.retrieve(customer_id)
        profile = Profile.objects.get(customer=customer_id)
        if customer.invoice_settings.default_payment_method:
            has_payment_method = True
    return render(request, 'payments/home.html', {"products": prod_list, "customer": customer_id, "profile": profile, 'has_payment_method': has_payment_method})

def complete(request):
    return render(request, "payments/complete.html")


# new
@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': STRIPE_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        price_id = request.GET.get('plan_id')
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create
            # Subscribe the user to the subscription created
            try:
                subscription = stripe.Subscription.create(
                    customer='cus_IbzMek57AM6ro8',
                    items=[
                        {
                            "price": price_id,
                        },
                    ],
                    expand=["latest_invoice.payment_intent"]
                )
                djstripe_subscription = djstripe.models.Subscription.sync_from_stripe_data(subscription)
                return JsonResponse(subscription)
            except:

                # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
                checkout_session = stripe.checkout.Session.create(
                    success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                    cancel_url=domain_url + 'cancelled/',
                    payment_method_types=['card'],
                    mode='payment',
                    line_items=[
                        {
                            "price": price_id,
                            "quantity": 1,
                        },
                    ]
                )
                return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)})

@csrf_exempt
def create_sub(request):
    if request.method == 'POST':
        # Reads application/json and returns a response
        data = request.body.decode('utf8').replace("'", '"')
        data = json.loads(data)
        payment_method = data['payment_method']
        try:
            customer = stripe.Customer.retrieve("cus_IbzMek57AM6ro8")
            djstripe_customer = djstripe.models.Customer.sync_from_stripe_data(customer)
            if payment_method:
                payment_method_obj = stripe.PaymentMethod.retrieve(payment_method)
                djstripe.models.PaymentMethod.sync_from_stripe_data(payment_method_obj)
                djstripe_customer.add_payment_method(payment_method_obj)

            # Subscribe the user to the subscription created
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {
                        "price": data["price_id"],
                    },
                ],
                expand=["latest_invoice.payment_intent"]
            )
            djstripe_subscription = djstripe.models.Subscription.sync_from_stripe_data(subscription)
            profile = Profile.objects.get(customer=customer.id)
            profile.subscription = djstripe_subscription.id
            profile.save()

            return JsonResponse(subscription)
        except Exception as e:
            return JsonResponse({'error': (e.args[0])}, status=403)
    else:
        return HttpResponse('requet method not allowed')



# TESTING CUSTOM STRIPE PORTAL
def customer_portal(request):
  customer_id = request.GET.get('customer_id')
    # Authenticate your user.
  session = stripe.billing_portal.Session.create(
    customer=customer_id,
    return_url='https://test.edilcloud.io/apps/dashboard',
  )
  return redirect(session.url)

@csrf_exempt
def my_webhook_view(request):
    webhook_secret = 'whsec_c5UDu75y55yZ2JRry8BGOEvZ8u0PNu7R'
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    if event_type == 'checkout.session.completed':
        # Payment is successful and the subscription is created.
        # You should provision the subscription.
        print(data)
    elif event_type == 'invoice.paid':
        # Continue to provision the subscription as payments continue to be made.
        # Store the status in your database and check when a user accesses your service.
        # This approach helps you avoid hitting rate limits.
        print(data)
    elif event_type == 'invoice.payment_failed':
        # The payment failed or the customer does not have a valid payment method.
        # The subscription becomes past_due. Notify your customer and send them to the
        # customer portal to update their payment information.
        print(data)
    else:
        print('Unhandled event type {}'.format(event.type))

    return JsonResponse({'status': 'success'})
