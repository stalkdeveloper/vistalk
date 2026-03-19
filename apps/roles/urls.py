# apps/roles/urls.py
from django.urls import path
from . import views

app_name = 'roles'

urlpatterns = [
    path('admin/roles/',                views.RoleListView.as_view(),   name='index'),
    path('admin/roles/create/',         views.RoleCreateView.as_view(), name='create'),
    path('admin/roles/<int:pk>/edit/',  views.RoleEditView.as_view(),   name='edit'),
    path('admin/roles/<int:pk>/delete/',views.RoleDeleteView.as_view(), name='delete'),
]