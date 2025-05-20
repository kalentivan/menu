from collections import defaultdict

from django.shortcuts import render, get_object_or_404

from tree_menu.models import Menu, MenuItem
from tree_menu.templatetags.draw_menu import update_absolute_urls


def menu_detail(request, menu_slug, path=None):
    """

    :param request:
    :param menu_slug:
    :param path: путь к пункту меню
    :return:
    """
    items = list(MenuItem.objects
                 .select_related('menu', 'parent')
                 .filter(menu__slug=menu_slug))
    menu_display_name = items[0].menu.name if items else menu_slug
    # Индексация по id
    item_by_id = {item.id: item for item in items}

    children_map = defaultdict(list)
    for item in items:
        children_map[item.parent_id].append(item)

    for item in items:
        item.children = children_map.get(item.id, [])

    items = update_absolute_urls(items)  # обновляем абсолютные пути
    opened_paths = set()
    current_item = None

    if path:
        path_parts = [p for p in path.split('/') if p]
        for item in items:
            if item.absolute_url.strip('/') == '/'.join(path_parts):
                current_item = item
                break

        if current_item:
            # Добавим в opened_paths цепочку родителей
            while current_item:
                opened_paths.add(current_item.id)
                current_item = item_by_id.get(current_item.parent_id)

    context = {
        'items_by_menu': {menu_display_name: items},    # объекты меню
        'menu_name': menu_display_name,
        'current_url': request.path,
        'opened_paths': opened_paths,
        'current_item': item_by_id.get(current_item.id) if current_item else None,
    }
    return render(request, 'tree_menu/menu_detail.html', context)


def menu_list(request):
    """
    Список всех меню
    :param request:
    :return:
    """
    # Загружаем все меню
    menus = Menu.objects.all()

    # Загружаем все MenuItem за один запрос
    all_items = list(MenuItem.objects.select_related('menu', 'parent'))

    # Сгруппируем элементы по имени меню
    items_by_menu = defaultdict(list)
    for item in all_items:
        items_by_menu[item.menu.name].append(item)

    # Вычислим абсолютные пути для всех элементов
    all_items = update_absolute_urls(all_items)

    # Обновим items_by_menu с элементами, у которых уже есть абсолютные пути
    for menu_name, items in items_by_menu.items():
        items_by_menu[menu_name] = [item for item in all_items if item.menu.name == menu_name]

    context = {
        'menus': menus,
        'items_by_menu': dict(items_by_menu),
    }
    return render(request, 'tree_menu/menu_list.html', context)

