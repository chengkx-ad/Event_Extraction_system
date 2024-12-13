from django.urls import path
from . import views

app_name = 'file_management'

urlpatterns = [
    # 文档管理
    path('documents/', views.document_list, name='document_list'),
    path('documents/<int:project_id>/upload/', views.document_upload, name='document_upload'),
    path('documents/<int:project_id>/<int:pk>/', views.document_detail, name='document_detail'),
    path('documents/<int:project_id>/<int:pk>/update/', views.document_update, name='document_update'),
    path('documents/<int:project_id>/<int:pk>/delete/', views.document_delete, name='document_delete'),
    path('documents/<int:project_id>/<int:pk>/assign/', views.document_assign, name='document_assign'),
    
    # 批次管理
    path('batches/<int:project_id>/', views.batch_list, name='batch_list'),
    path('batches/<int:project_id>/create/', views.batch_create, name='batch_create'),
    path('batches/<int:project_id>/<int:pk>/', views.batch_detail, name='batch_detail'),
    path('batches/<int:project_id>/<int:pk>/update/', views.batch_update, name='batch_update'),
    path('batches/<int:project_id>/<int:pk>/delete/', views.batch_delete, name='batch_delete'),
    path('batches/<int:project_id>/<int:pk>/add-documents/', views.batch_add_documents, name='batch_add_documents'),
    path('batches/<int:project_id>/<int:pk>/remove-document/<int:doc_pk>/', 
         views.batch_remove_document, name='batch_remove_document'),
] 