from django.views import View
import stripe
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