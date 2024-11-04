from django.core.management.base import BaseCommand
from decimal import Decimal
from faker import Faker
import random
from home.models import Merchant
from transaction.models import Transaction

class Command(BaseCommand):
    help = 'Generate 200 transactions with fake data for testing purposes'

    def handle(self, *args, **kwargs):
        fake = Faker()
        merchants = list(Merchant.objects.filter(balance__gt=0))

        if len(merchants) < 2:
            self.stdout.write(self.style.ERROR("Not enough merchants with balance for transactions"))
            return

        statuses = ['pending', 'approved', 'rejected']
        
        for _ in range(200):
            sender = random.choice(merchants)
            receiver = random.choice([m for m in merchants if m != sender])
            amount = round(Decimal(random.uniform(1, float(sender.balance))), 2)
            status = random.choice(statuses)
            approver = fake.name()

            transaction = Transaction(
                sender=sender,
                receiver=receiver,
                amount=amount,
                status=status,
                approver=approver,
            )
            try:
                transaction.save()
                self.stdout.write(self.style.SUCCESS(f"Transaction created: {transaction.id}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create transaction: {e}"))

        self.stdout.write(self.style.SUCCESS("200 transactions created successfully"))
