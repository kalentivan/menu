from django.core.management.base import BaseCommand
from tree_menu.models import Menu, MenuItem
import random
import string
import uuid6

WORDS = ["Home", "About", "Contact", "Blog", "Shop", "News", "FAQ", "Support", "Team", "Careers", "Products"]

class Command(BaseCommand):
    help = 'Генерирует случайные меню и пункты меню'

    def add_arguments(self, parser):
        parser.add_argument('--num-menus', type=int, default=3, help='Количество меню для создания')
        parser.add_argument('--max-items', type=int, default=5, help='Максимальное количество пунктов на уровень')
        parser.add_argument('--max-depth', type=int, default=3, help='Максимальная глубина вложенности')

    def generate_random_string(self, length=8):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def generate_random_menu_name(self):
        return f"menu_{self.generate_random_string(5)}"

    def generate_random_item_title(self):
        return f"{random.choice(WORDS)} {self.generate_random_string(3)}"

    def generate_random_url(self):
        return f"item_{self.generate_random_string(5)}"

    def create_random_menus(self, num_menus, max_items, max_depth):
        Menu.objects.all().delete()
        MenuItem.objects.all().delete()

        for _ in range(num_menus):
            menu = Menu.objects.create(
                id=uuid6.uuid7(),
                name=self.generate_random_menu_name()
            )

            def create_items(parent=None, depth=0):
                if depth >= max_depth:
                    return

                num_items = random.randint(1, max_items)
                for _ in range(num_items):
                    item = MenuItem.objects.create(
                        id=uuid6.uuid7(),
                        menu=menu,
                        parent=parent,
                        title=self.generate_random_item_title(),
                        url=self.generate_random_url()
                    )
                    if random.random() > 0.5:
                        create_items(parent=item, depth=depth + 1)

            create_items()

    def handle(self, *args, **options):
        num_menus = options['num_menus']
        max_items = options['max_items']
        max_depth = options['max_depth']
        self.create_random_menus(num_menus, max_items, max_depth)
        self.stdout.write(self.style.SUCCESS(f'Успешно создано {num_menus} случайных меню!'))
