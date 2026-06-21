from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('group/create/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/add-member/', views.add_member, name='add_member'),
    path('group/<int:group_id>/remove-member/<int:user_id>/', views.remove_member, name='remove_member'),
]
