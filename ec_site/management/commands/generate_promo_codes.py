import random
import string
from django.core.management.base import BaseCommand
from ec_site.models import PromoCode
class Command(BaseCommand):
    help='10個のプロモーションコードを作成します'

    def handle(self, *args, **options):
        for _ in range(10):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            discount = random.randint(100,1000)

            PromoCode.objects.create(
                code=code,
                discount_amount=discount,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f"作成: {code} - {discount}円割引"))