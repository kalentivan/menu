from collections import defaultdict
from typing import List

from django import template
from django.core.cache import cache
from django.utils.safestring import mark_safe
from pytils.translit import slugify

from tree_menu.models import MenuItem

register = template.Library()


def build_tree(items: List[MenuItem]) -> defaultdict[str, List]:
    """
    Построение дерева элементов
    :param items:
    :return:
    """
    tree = defaultdict(list)
    for item in items:
        parent_id = item.parent_id if item.parent_id else None
        tree[parent_id].append(item)
    return tree


def render_menu(items_tree,
                parent_id: str | None,
                current_url: str,
                opened_paths: set[str],
                level: int = 0):
    """
    Генерируем HTML меню
    :param items_tree:
    :param parent_id:
    :param current_url:
    :param opened_paths:
    :param level:
    :return:
    """
    is_hidden = level > 0 and parent_id not in opened_paths
    html = "<ul class='menu-list'>" if level == 0 else f"<ul class='submenu-list{' hidden' if is_hidden else ''}'>"

    for item in items_tree.get(parent_id, []):
        is_active = current_url == item.absolute_url
        is_open = item.id in opened_paths
        classes = ['menu-item']
        if is_active:
            classes.append('active')
        if is_open:
            classes.append('open')
        html += f"<li class='{' '.join(classes)}' data-item-id='{item.id}'>"
        html += f"<div class='flex items-center'>"
        html += f"<a href='{item.absolute_url}' class='menu-item-title block py-2 px-4 hover:bg-gray-100 cursor-pointer'>{item.title}</a>"
        if items_tree.get(item.id):
            toggle_symbol = '−' if is_open else '+'
            html += f"<span class='text-blue-600 hover:text-blue-800 ml-2'>{toggle_symbol}</span>"
        html += "</div>"
        if items_tree.get(item.id):
            html += render_menu(items_tree, item.id, current_url, opened_paths, level + 1)
        html += "</li>"
    html += "</ul>"
    return html


@register.simple_tag(takes_context=True)
def draw_menu(context: dict,
              menu_name: str):
    """
    Отрисовка одного меню
    :param context:
    :param menu_name:
    :return:
    """
    request = context.get('request')
    cache_key = slugify(f'menu_{menu_name}_{request.path}_tag')  # ключ для кеширования
    items = context.get("items_by_menu", dict()).get(menu_name)  # берем предварительно загруженные элементы
    if items is None:
        # если их нет - подгружаем
        items = MenuItem.objects.select_related('parent', 'menu').filter(menu__name=menu_name)
        items = update_absolute_urls(list(items))  #
    if items is None:   # все равно нет - нет данных
        result = f"<div class='menu-error'>Меню '{menu_name}' не найдено</div>"
        cache.set(cache_key, result, timeout=3600)
        return mark_safe(result)

    resolved_urls = {item.id: item.absolute_url for item in items}
    current_url = request.path
    opened_paths = set()

    # определяем, какие пути надо раскрыть
    for item in items:
        if current_url == resolved_urls[item.id]:
            opened_paths.add(item.id)
            parent = item.parent
            while parent:
                opened_paths.add(parent.id)
                parent = parent.parent
            break

    items = update_absolute_urls(items)
    tree = build_tree(items)
    result = render_menu(tree, None, current_url, opened_paths)
    cache.set(cache_key, result, timeout=3600)
    return mark_safe(result)


def update_absolute_urls(menu_items: List[MenuItem]):
    """
    Обновляем пути в цикле у всех сразу, чтобы не делать много запросов для получения каждого пути
    :param menu_items:
    :return:
    """
    menu_dict = {item.id: item for item in menu_items}

    # Вычисляем абсолютные URL-ы
    for item in menu_items:
        path_parts = []
        current = item
        while current:
            path_parts.append(slugify(current.title))
            current = menu_dict.get(current.parent_id)
        path_parts.reverse()
        item.absolute_url = f"/{item.menu.slug}/" + "/".join(path_parts) + "/"

    return menu_items
