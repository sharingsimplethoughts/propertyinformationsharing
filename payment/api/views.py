from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .serializers import *
from common_method.validators import get_error
import logging

logger = logging.getLogger('payments')
from accounts.middleware import ValidateJWTToken

from accounts.models import Company

# payment gateway
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def make_payment(request, *args, **kwargs):

    ### all logic for payment
    data = request.data
    serializer = PaymentSerializer(data=data)
    if serializer.is_valid():
        try:
            customer = get_or_create_customer(
                request.user,
                data['card_token'],
                serializer.data['is_card_save']
            )
            company_obj = Company.objects.get(user=request.user)
            plan_price = company_obj.bussiness_area.subscription.price
            plan_in_cent = plan_price * 100
            charge = stripe.Charge.create(
                amount=int(plan_in_cent),
                currency='usd',
                customer=customer,  # customer id
                description='Payment to buy subscription plan'
            )
            print(charge, 'charge', charge.outcome.seller_message)
            if charge:
                payment_history = PaymentHistory.objects.create(user=request.user,
                                                                payment_type='1',
                                                                description="Payment to buy subscription plan",
                                                                status_message=charge.outcome.seller_message,
                                                                payment_id=charge.id,
                                                                amount=plan_price,
                                                                captured=charge.captured,
                                                                payment_detail=customer)

                company_obj.is_subscription_plan_active = True
                company_obj.save()

                return Response({
                    'message': 'Paid successfully'
                }, status=200)

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})

            print("Status is: %s" % e.http_status)
            print("Type is: %s" % err.get('type'))
            print("Code is: %s" % err.get('code'))
            print("Param is: %s" % err.get('param'))
            print("Message is: %s" % err.get('message'))
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            body = e.json_body
            err = body.get('error', {})
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            body = e.json_body
            err = body.get('error', {})
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            body = e.json_body
            err = body.get('error', {})
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            body = e.json_body
            err = body.get('error', {})
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            body = e.json_body
            err = body.get('error', {})
        except Exception as e:
            # Something else happened, completely unrelated to Stripe

            err = {'message': e}

        ### save payment 

        PaymentHistory.objects.create(user=request.user, payment_type='1',
                                      description="Payment to buy subscription",
                                      status_message=err.get('message'))

        return Response({
            'status': 'error',
            'message': err.get('message')
        }, status=400)

    return Response({'message': get_error(serializer)}, 400)


class Make_Payment(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request, *args, **kwargs):
        return make_payment(request, *args, **kwargs)


def get_or_create_customer(user, token, is_card_save):
    customer_qs = StripeCustomer.objects.filter(user=user, card_token=token)
    if customer_qs.exists():
        return customer_qs.first().stripe_cus_id

    customer = stripe.Customer.create(
        email=user.email,
        source=token,
        name=user.name,
    )
    print(customer)
    if is_card_save == 'true' or is_card_save == True:
        card = 'XXXX-XXXX-XXXX-' + customer.sources.data[0].last4
        name = customer.sources.data[0].name
        StripeCustomer.objects.create(user=user, card_type=customer.sources.data[0].brand,
                                      exp_month=customer.sources.data[0].exp_month,
                                      exp_year=customer.sources.data[0].exp_year, name=name, card_token=token,
                                      stripe_cus_id=customer.id, card=card)
    return customer.id


class ListOfSavedCard(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request, *args, **kwargs):
        qs = StripeCustomer.objects.filter(user=request.user)
        data = ListOfSavedCardSerializer(qs, many=True).data

        return Response({
            'message': 'success',
            'data': data
        }, 200)


class SaveNewCardAPIView(APIView):
    permission_classes = (IsAuthenticated, ValidateJWTToken,)
    authentication_classes = [JSONWebTokenAuthentication]

    def post(self, request):
        token = request.data.get('card_token')
        if token:
            user = request.user
            try:
                customer = stripe.Customer.create(
                    email=user.email,
                    source=token,
                    name=user.name,
                )

                card = 'XXXX-XXXX-XXXX-' + customer.sources.data[0].last4
                name = customer.sources.data[0].name
                StripeCustomer.objects.create(user=user, card_type=customer.sources.data[0].brand,
                                              exp_month=customer.sources.data[0].exp_month,
                                              exp_year=customer.sources.data[0].exp_year, name=name, card_token=token,
                                              stripe_cus_id=customer.id, card=card)

                return Response({
                    'message': 'Card added successfully'

                }, 200)

            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                body = e.json_body
                err = body.get('error', {})
                print("Status is: %s" % e.http_status)
                print("Type is: %s" % err.get('type'))
                print("Code is: %s" % err.get('code'))
                print("Param is: %s" % err.get('param'))
                print("Message is: %s" % err.get('message'))
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                body = e.json_body
                err = body.get('error', {})
            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                body = e.json_body
                err = body.get('error', {})
            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                body = e.json_body
                err = body.get('error', {})
            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                body = e.json_body
                err = body.get('error', {})
            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                body = e.json_body
                err = body.get('error', {})
            except Exception as e:
                # Something else happened, completely unrelated to Stripe
                err = {'message': e}
                print(err)
            return Response({
                'message': err.get('message')
            }, 400)
        return Response({
            'message': 'Please provide source token'
        }, 400)
