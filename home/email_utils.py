from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_order_confirmation_email(order):
    subject = f'Order Confirmation - Order #{order.id}'
    context = {
        'order': order,
        'items': order.items.all(),
    }
    html_message = render_to_string('emails/order_confirmation.html', context)
    plain_message = render_to_string('emails/order_confirmation.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message
    )

def send_order_status_update_email(order):
    subject = f'Order Status Update - Order #{order.id}'
    context = {
        'order': order,
        'status': order.get_status_display(),
    }
    html_message = render_to_string('emails/order_status_update.html', context)
    plain_message = render_to_string('emails/order_status_update.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message
    )

def send_refund_confirmation_email(order):
    subject = f'Refund Confirmation - Order #{order.id}'
    context = {
        'order': order,
        'refund_amount': order.total_price,
    }
    html_message = render_to_string('emails/refund_confirmation.html', context)
    plain_message = render_to_string('emails/refund_confirmation.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message
    ) 