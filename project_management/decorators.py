from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Project, ProjectMembership

def project_role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            project_id = kwargs.get('project_id') or kwargs.get('pk')
            if not project_id:
                return redirect('project_management:project_list')
            
            try:
                project = Project.objects.get(id=project_id)
                membership = ProjectMembership.objects.get(
                    project=project,
                    user=request.user
                )
                
                if membership.role not in allowed_roles:
                    messages.error(request, '您没有执行此操作的权限')
                    return redirect('project_management:project_detail', pk=project_id)
                    
                return view_func(request, *args, **kwargs)
                
            except (Project.DoesNotExist, ProjectMembership.DoesNotExist):
                messages.error(request, '项目不存在或您不是项目成员')
                return redirect('project_management:project_list')
                
        return _wrapped_view
    return decorator

def annotation_permission_required(permission_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            document_id = kwargs.get('document_id')
            if not document_id:
                return redirect('annotation:task_list')
            
            try:
                document = Document.objects.select_related('project').get(id=document_id)
                membership = ProjectMembership.objects.get(
                    project=document.project,
                    user=request.user
                )
                
                if permission_type == 'annotate' and membership.role != 'annotator':
                    messages.error(request, '只有标注者可以执行此操作')
                    return redirect('annotation:task_list')
                    
                if permission_type == 'review' and membership.role != 'reviewer':
                    messages.error(request, '只有审核者可以执行此操作')
                    return redirect('annotation:review_list')
                    
                return view_func(request, *args, **kwargs)
                
            except (Document.DoesNotExist, ProjectMembership.DoesNotExist):
                messages.error(request, '文档不存在或您不是项目成员')
                return redirect('annotation:task_list')
                
        return _wrapped_view
    return decorator 