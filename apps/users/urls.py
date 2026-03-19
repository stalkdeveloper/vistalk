from django.urls import path
from . import views

app_name = 'users'
 
urlpatterns = [
    path('admin/users/',                    views.UserListView.as_view(),         name='index'),
    path('admin/users/create/',             views.UserCreateView.as_view(),       name='create'),
    path('admin/users/<int:pk>/edit/',      views.UserEditView.as_view(),         name='edit'),
    path('admin/users/<int:pk>/delete/',    views.UserDeleteView.as_view(),       name='delete'),
    path('admin/users/<int:pk>/toggle/',    views.UserToggleActiveView.as_view(), name='toggle'),
]