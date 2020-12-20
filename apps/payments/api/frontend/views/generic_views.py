from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from web import settings

class GenericPlansViews(APIView):
    def get(self, request):
        """
        Get Plans Pricing
        :param request:
        :return:
        """
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe_prices = stripe.Price.list()
        complete_list = []
        for price in stripe_prices.data:
            product = stripe.Product.retrieve(price['product'])
            product['price'] = price
            complete_list.append(product)
        # plans = stripe.Plan.list()
        return Response(
            complete_list,
            status=status.HTTP_200_OK
        )


import stripe
from django.http import HttpRequest, JsonResponse

class GenericCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        customer = request.user  # get customer model based off request.user
        data = request.data
        if 'price_id' in data and 'customer_id' in data:
            price_id = data['price_id']
            customer_id = data['customer_id']
            if request.method == 'POST':
                # Assign product price_id, to support multiple products you
                # can include a product indicator in the incoming POST data

                # Set Stripe API key
                stripe.api_key = settings.STRIPE_SECRET_KEY

                # Create Stripe Checkout session
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    mode="subscription",
                    line_items=[
                        {
                            "price": price_id,
                            "quantity": 1
                        }
                    ],
                    customer=customer_id,
                    success_url="https://edilcloud.it/payment/success?sessid={{CHECKOUT_SESSION_ID}}",
                    cancel_url="https://edilcloud.it/payment/cancel",
                    # The cancel_url is typically set to the original product page
                )
            return Response(
                {'sessionId': checkout_session['id']},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                "Error: No price or customer selected!",
                status=status.HTTP_400_BAD_REQUEST
            )
