from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import TestModel, Product, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .serializers import ProductSerializer, CartItemSerializer, UserSerializer, OrderSerializer, CreateOrderSerializer, OrderItemSerializer
from django.contrib.auth import get_user_model
from .forms import CheckoutForm
from decimal import Decimal
import stripe
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

User = get_user_model()

def home(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            TestModel.objects.create(name=name)
            return redirect('home')
    
    items = TestModel.objects.all().order_by('-created_at')
    return render(request, 'home/index.html', {'items': items})

def delete_item(request, item_id):
    item = get_object_or_404(TestModel, id=item_id)
    item.delete()
    return redirect('home')

def product_list(request):
    products = Product.objects.all()
    cart_items_count = CartItem.objects.filter(user=request.user).count() if request.user.is_authenticated else 0
    return render(request, 'home/product_list.html', {
        'products': products,
        'cart_items_count': cart_items_count
    })

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'home/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': 1}
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('product_list')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    action = request.POST.get('action')
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    cart_item.save()
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('cart')
    
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = total
            order.save()
            
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            
            cart_items.delete()
            return redirect('order_confirmation', order_id=order.id)
    else:
        form = CheckoutForm()
    
    return render(request, 'home/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total,
        'stripe_public_key': settings.STRIPE_PUBLISHABLE_KEY
    })

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'home/order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'home/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'home/order_detail.html', {'order': order})

@login_required
def request_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        if order.payment_status == 'paid' and order.status != 'cancelled':
            try:
                # Create Stripe refund
                refund = stripe.Refund.create(
                    payment_intent=order.stripe_payment_intent_id
                )
                
                if refund.status == 'succeeded':
                    order.payment_status = 'refunded'
                    order.status = 'cancelled'
                    order.save()
                    
                    # Send refund confirmation email
                    send_refund_confirmation_email(order)
                    
                    messages.success(request, 'Refund processed successfully.')
                    return redirect('order_detail', order_id=order.id)
                    
            except stripe.error.StripeError as e:
                messages.error(request, f'Error processing refund: {str(e)}')
        else:
            messages.error(request, 'This order cannot be refunded.')
    
    return redirect('order_detail', order_id=order.id)

@login_required
def profile(request):
    return render(request, 'home/profile.html', {
        'user': request.user
    })

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CartItem.objects.filter(user=self.request.user)
        return CartItem.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def total(self, request):
        if request.user.is_authenticated:
            total = sum(item.get_total_price() for item in self.get_queryset())
            return Response({'total': total})
        return Response({'total': 0})

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            return Response({'status': 'Order cancelled'})
        return Response(
            {'error': 'Only pending orders can be cancelled'},
            status=status.HTTP_400_BAD_REQUEST
        )

class StripeWebhookView(APIView):
    permission_classes = []  # No authentication required for webhooks

    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            order_id = payment_intent.metadata.get('order_id')
            if order_id:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'paid'
                order.save()

        return Response(status=status.HTTP_200_OK)

# API Views for specific actions
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def cart_total(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price for item in cart_items)
    return Response({'total': total})

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_to_cart_api(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order = Order.objects.get(payment_intent_id=payment_intent.id)
        order.payment_status = 'completed'
        order.save()

    return HttpResponse(status=200)
