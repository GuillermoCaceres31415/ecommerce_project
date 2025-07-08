from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

class Command(BaseCommand):
    help = 'Create Users and Moderators groups with their permissions'

    def handle(self, *args, **options):

        Group.objects.filter(name='Users').delete()
        Group.objects.filter(name='Moderators').delete()


        users_group, _ = Group.objects.get_or_create(name='Users')
        moderators_group, _ = Group.objects.get_or_create(name='Moderators')

        # ---- Permessi per Users ----

        Product = apps.get_model('products', 'Product')
        ct_product = ContentType.objects.get_for_model(Product)
        view_product = Permission.objects.get(
            codename='view_product',
            content_type=ct_product
        )
        users_group.permissions.add(view_product)


        CartItem = apps.get_model('products', 'CartItem')
        ct_cartitem = ContentType.objects.get_for_model(CartItem)
        for codename in ['add_cartitem', 'change_cartitem', 'delete_cartitem', 'view_cartitem']:
            perm = Permission.objects.get(codename=codename, content_type=ct_cartitem)
            users_group.permissions.add(perm)

        Order = apps.get_model('products', 'Order')
        ct_order = ContentType.objects.get_for_model(Order)
        for codename in ['add_order', 'change_order', 'view_order']:
            perm = Permission.objects.get(codename=codename, content_type=ct_order)
            users_group.permissions.add(perm)

        # ---- Permessi aggiuntivi per Moderators ----

        moderators_group.permissions.set(users_group.permissions.all())


        CustomUser = apps.get_model('accounts', 'CustomUser')
        ct_user = ContentType.objects.get_for_model(CustomUser)
        for codename in ['change_customuser', 'delete_customuser']:
            perm = Permission.objects.get(codename=codename, content_type=ct_user)
            moderators_group.permissions.add(perm)

        self.stdout.write(self.style.SUCCESS(
            ' Gruppi "Users" e "Moderators" creati con i permessi corretti'
        ))
