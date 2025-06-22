from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Create user groups and assign permissions'

    def handle(self, *args, **options):
        # Crea gruppo Moderators
        moderators_group, created = Group.objects.get_or_create(name='Moderators')

        if created:
            self.stdout.write(self.style.SUCCESS('Created Moderators group'))
        else:
            self.stdout.write('Moderators group already exists')

        # Aggiungi permessi ai moderatori
        moderator_permissions = [
            'add_product', 'change_product', 'delete_product',
            'delete_customuser', 'change_customuser'
        ]

        permissions_added = 0
        for perm in moderator_permissions:
            try:
                permission = Permission.objects.get(codename=perm)
                moderators_group.permissions.add(permission)
                permissions_added += 1
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Permission {perm} does not exist')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'Added {permissions_added} permissions to Moderators group'
            )
        )