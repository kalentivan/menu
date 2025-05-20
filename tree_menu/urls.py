from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.menu_list, name='menu_list'),
    re_path(r'^(?P<menu_slug>[^/]+)/(?P<path>.*)?$', views.menu_detail, name='menu_detail'),
]
