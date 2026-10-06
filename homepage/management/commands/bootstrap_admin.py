import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create or update the RNT Home Builder admin from environment variables.'

    def handle(self, *args, **options):
        username = os.getenv('RNT_ADMIN_USERNAME', '').strip()
        email = os.getenv('RNT_ADMIN_EMAIL', '').strip()
        password = os.getenv('RNT_ADMIN_PASSWORD', '').strip()
        if not username or not password:
            self.stdout.write('RNT admin bootstrap skipped: RNT_ADMIN_USERNAME/RNT_ADMIN_PASSWORD not set.')
            return
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        changed = created
        if email and user.email != email:
            user.email = email
            changed = True
        if not user.is_staff or not user.is_superuser:
            user.is_staff = True
            user.is_superuser = True
            changed = True
        user.set_password(password)
        changed = True
        if changed:
            user.save()
        self.stdout.write(self.style.SUCCESS(f'RNT admin ready: {username}'))
