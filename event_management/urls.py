from django.urls import path
from . import views

app_name = 'event_management'

urlpatterns = [
    path('types/<int:project_id>/', views.event_type_list, name='event_type_list'),
    path('types/<int:project_id>/create/', views.event_type_create, name='event_type_create'),
    path('types/<int:project_id>/<int:pk>/', views.event_type_detail, name='event_type_detail'),
    path('types/<int:project_id>/<int:pk>/update/', views.event_type_update, name='event_type_update'),
    path('types/<int:project_id>/<int:pk>/delete/', views.event_type_delete, name='event_type_delete'),
    
    path('types/<int:project_id>/<int:event_type_id>/arguments/add/', 
         views.argument_role_create, name='argument_role_create'),
    path('types/<int:project_id>/<int:event_type_id>/arguments/<int:pk>/update/', 
         views.argument_role_update, name='argument_role_update'),
    path('types/<int:project_id>/<int:event_type_id>/arguments/<int:pk>/delete/', 
         views.argument_role_delete, name='argument_role_delete'),
] 