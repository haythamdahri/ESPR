import datetime
from decimal import Decimal

from django.core.mail import send_mail
from paypal.standard.models import ST_PP_COMPLETED
from django.shortcuts import get_object_or_404
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from .models import Order, OrderLine, Stock

#from django.dispatch import receiver

#from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged, payment_was_refunded, payment_was_reversed


"""def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    # You need to check 'payment_status' of the IPN
    print('notify')
    print('payment_status : {}'.format(ipn_obj.payment_status))
    print('Receiver_email : {}'.format(ipn_obj.receiver_email))
    print('custom : {}'.format(ipn_obj.custom))
    print('mc gross : {}'.format(ipn_obj.mc_gross))
    print('invoice : {}'.format(ipn_obj.invoice))
    print('Mc Shipping : {}'.format(ipn_obj.mc_shipping))
    print('Num Cart Items : {}'.format(ipn_obj.num_cart_items))
    print('Payer Status : {}'.format(ipn_obj.payer_status))
    print('Payment Date : {}'.format(ipn_obj.payment_date))
    print('Pending Reason : {}'.format(ipn_obj.pending_reason))
    print('Payment Type : {}'.format(ipn_obj.payment_type))
    print('Address Country : {}'.format(ipn_obj.address_country))
    print('Address Name : {}'.format(ipn_obj.address_name))
    if ipn_obj.payment_status == "Completed":
        print('completed')
        # Undertake some action depending upon `ipn_obj`.
        if ipn_obj.custom == "Upgrade all users!":
            print('upgrade')
    else:
        print('not completed')


payment_was_successful.connect(show_me_the_money)
payment_was_flagged.connect(show_me_the_money)
payment_was_refunded.connect(show_me_the_money)
payment_was_reversed.connect(show_me_the_money)
"""


def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    print('notify')
    print('payment_status : {}'.format(ipn_obj.payment_status))
    print('Receiver_email : {}'.format(ipn_obj.receiver_email))
    print('custom : {}'.format(ipn_obj.custom))
    print('mc gross : {}'.format(ipn_obj.mc_gross))
    print('invoice : {}'.format(ipn_obj.invoice))
    print('Mc Shipping : {}'.format(ipn_obj.mc_shipping))
    print('Num Cart Items : {}'.format(ipn_obj.num_cart_items))
    print('Payer Status : {}'.format(ipn_obj.payer_status))
    print('Payment Date : {}'.format(ipn_obj.payment_date))
    print('Pending Reason : {}'.format(ipn_obj.pending_reason))
    print('Payment Type : {}'.format(ipn_obj.payment_type))
    print('Address Country : {}'.format(ipn_obj.address_country))
    print('Address Name : {}'.format(ipn_obj.address_name))
    order = get_object_or_404(Order, pk=1)
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        if ipn_obj.receiver_email == "karimelkhaoua_espr@gmail.com":
            if Decimal(ipn_obj.mc_gross) == Decimal(order.amount):
                if ipn_obj.mc_currency == 'USD':
                    order_line = OrderLine.objects.filter(order=order)
                    for el in order_line:
                        stock_results = Stock.objects.filter(product=el.product, color=el.color)
                        if stock_results.exists():
                            stock = stock_results[0]
                            stock.quantity = stock.quantity - el.quantity
                            stock.save()
                            print('stock saved')
                    order.status = "Processing"
                    order.date_payment = datetime.date.today()
                    order.save()
                    message = "<p>Bonjour,</p><p>Votre Commande <b>#{}</b> :</p>" \
                              "<p>Montant : <b>{}</b></p>" \
                              "<p>Date : <b>{}</b></p>" \
                              "<p>Date de Paiement : <b>{}</b></p>" \
                              "<p>Méthode de Paiement : <b>Paypal</b></p>" \
                              "<p>Méthode de Livraison : <b>{}</b></p>" \
                              "<p>a été correctement payé, et elle sera traitée très prochainement." \
                              "<p>Merci.</p>".format(order.pk, order.amount, order.date, order.date_payment, order.delivery_method)
                    print('message écrit..')
                    print('command réussi')
                else:
                    message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> :</p>" \
                              "<p>a été refusé car vous avais utilisé le devis {} au lieu de MAD" \
                              "<p>Merci.</p>".format(order.pk, ipn_obj.mc_currency)
                    print('message écrit..')
            else:
                message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> :</p>" \
                          "<p>a été refusé car vous n'avais pas payé toute la somme {} Dh." \
                          "<p>Merci.</p>".format(order.pk, order.amount)
                print('message écrit..')
        else:
            message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> :</p>" \
                      "<p>a été refusé car vous n'avais pas payé le vrai compte." \
                      "<p>Merci.</p>".format(order.pk, order.amount)
            print('message écrit..')
    elif ipn_obj.payment_status == "Pending":
        message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> :</p>" \
                  "<p>Votre Transaction est en cours de vérification par Paypal, raison : {}." \
                  "<p>Merci.</p>".format(order.pk, ipn_obj.pending_reason)
    else:
        message = "<p>Bonjour,</p><p>Votre paiement pour la Commande <b>#{}</b> a été refusé</p>".format(order.pk)
        print('message écrit..')
    send_mail(
        'Commande #{}'.format(order.pk),
        message,
        'admin@socifly.com',
        [order.user.user.email],
        fail_silently=False,
        html_message=message,
    )
    print('email envoyé')


valid_ipn_received.connect(show_me_the_money)
invalid_ipn_received.connect(show_me_the_money)
