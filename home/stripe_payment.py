import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(order):
    try:
        # Convert total_price to cents for Stripe
        amount = int(order.total_price * 100)
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            metadata={
                'order_id': order.id,
                'user_id': order.user.id
            }
        )
        
        # Update order with payment intent ID
        order.stripe_payment_intent_id = intent.id
        order.save()
        
        return {
            'client_secret': intent.client_secret,
            'publishable_key': settings.STRIPE_PUBLISHABLE_KEY
        }
    except Exception as e:
        return {'error': str(e)}

def confirm_payment(order):
    try:
        payment_intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
        
        if payment_intent.status == 'succeeded':
            order.payment_status = 'paid'
            order.status = 'processing'
            order.save()
            return True
        return False
    except Exception as e:
        return False 