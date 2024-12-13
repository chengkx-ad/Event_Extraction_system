from django.urls import path
from . import views

app_name = 'project_management'

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('<int:pk>/', views.project_detail, name='project_detail'),
    path('<int:pk>/update/', views.project_update, name='project_update'),
    path('<int:pk>/members/add/', views.add_member, name='add_member'),
    path('<int:pk>/members/<int:member_pk>/remove/', views.remove_member, name='remove_member'),
    path('register/', views.register, name='register'),
    path('change-password/', views.change_password, name='change_password'),
] 