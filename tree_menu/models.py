from typing import Optional

import uuid6
from django.db import models
from django.db.models import UUIDField
from pytils.translit import slugify


class Menu(models.Model):
    id = UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(null=True, unique=True, blank=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    id = UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    title = models.CharField(max_length=100)
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='menuitem_set')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    url = models.CharField(max_length=255, blank=True, help_text="Введите относительный URL, например /pasta/")
    named_url = models.CharField(max_length=255, blank=True, help_text="Имя маршрута, зарегистрированного в urls.py")

    absolute_url = ""   # абсолютный путь - собирается перед рендингом меню
    parent_id: Optional[uuid6.UUID]  # подсказка для PyCharm
    menu_id: Optional[uuid6.UUID]  # подсказка для PyCharm

    def __str__(self):
        return self.title
