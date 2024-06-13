from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Wallet, WalletHistory
from decimal import Decimal

@receiver(post_save, sender=Wallet)
def update_wallet_history(sender, instance, **kwargs):
    if instance.pk:
        try:
            previous = Wallet.objects.get(pk=instance.pk)
            print(previous)
        except Wallet.DoesNotExist:
            previous = None

        if previous:
            print('iam in previous')
            # Ensure both amounts are Decimal
            current_amount = Decimal(instance.amount)
            previous_amount = previous.previous_balance
            difference = current_amount - previous_amount
            print(difference)
            if difference != 0:
                transaction_type = 'credit' if difference > 0 else 'debit'
                WalletHistory.objects.create(
                    wallet=instance,
                    amount=abs(difference),
                    transaction_type=transaction_type
                )

