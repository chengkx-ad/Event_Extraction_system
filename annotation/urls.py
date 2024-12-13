from django.urls import path
from . import views

app_name = 'annotation'

urlpatterns = [
    # 标注任务列表
    path('tasks/', views.annotation_task_list, name='task_list'),
    path('tasks/completed/', views.completed_task_list, name='completed_task_list'),
    
    # 标注操作
    path('document/<int:document_id>/', views.annotate_document, name='annotate_document'),
    path('document/<int:document_id>/submit/', views.submit_annotation, name='submit_annotation'),
    path('document/<int:document_id>/events/add/', views.add_event, name='add_event'),
    path('document/<int:document_id>/events/<int:event_id>/update/', 
         views.update_event, name='update_event'),
    path('document/<int:document_id>/events/<int:event_id>/delete/', 
         views.delete_event, name='delete_event'),
    path('document/<int:document_id>/events/<int:event_id>/arguments/add/', 
         views.add_argument, name='add_argument'),
    path('document/<int:document_id>/events/<int:event_id>/arguments/<int:argument_id>/update/', 
         views.update_argument, name='update_argument'),
    path('document/<int:document_id>/events/<int:event_id>/arguments/<int:argument_id>/delete/', 
         views.delete_argument, name='delete_argument'),
    path('document/<int:document_id>/events/<int:event_id>/arguments/form/', views.get_argument_form, name='get_argument_form'),
    
    # 审核功能
    path('review/', views.review_list, name='review_list'),
    path('review/<int:annotation_id>/', views.review_annotation, name='review_annotation'),
    path('review/<int:annotation_id>/submit/', views.submit_review, name='submit_review'),
] 