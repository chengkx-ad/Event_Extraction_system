from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from project_management.models import Project
from .models import EventType, ArgumentRole
from .forms import EventTypeForm, ArgumentRoleForm
from project_management.decorators import project_role_required

@login_required
def event_type_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    event_types = project.event_types.all()
    context = {
        'project': project,
        'event_types': event_types,
    }
    return render(request, 'event_management/event_type_list.html', context)

@login_required
def event_type_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    if request.method == 'POST':
        form = EventTypeForm(request.POST)
        if form.is_valid():
            event_type = form.save(commit=False)
            event_type.project = project
            event_type.save()
            messages.success(request, '事件类型创建成功！')
            return redirect('event_management:event_type_detail', project_id=project.id, pk=event_type.pk)
    else:
        form = EventTypeForm()
    
    return render(request, 'event_management/event_type_form.html', {
        'form': form,
        'project': project,
    })

@login_required
@project_role_required(['admin'])
def event_type_detail(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    event_type = get_object_or_404(EventType, pk=pk, project=project)
    
    context = {
        'project': project,
        'event_type': event_type,
    }
    return render(request, 'event_management/event_type_detail.html', context)

@login_required
def event_type_update(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    event_type = get_object_or_404(EventType, pk=pk, project=project)
    
    if request.method == 'POST':
        form = EventTypeForm(request.POST, instance=event_type)
        if form.is_valid():
            form.save()
            messages.success(request, '事件类型更新成功！')
            return redirect('event_management:event_type_detail', project_id=project.id, pk=event_type.pk)
    else:
        form = EventTypeForm(instance=event_type)
    
    return render(request, 'event_management/event_type_form.html', {
        'form': form,
        'project': project,
        'event_type': event_type,
    })

@login_required
def event_type_delete(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没���权限访问此项目！')
        return redirect('project_management:project_list')
    
    event_type = get_object_or_404(EventType, pk=pk, project=project)
    if request.method == 'POST':
        event_type.delete()
        messages.success(request, '事件类型删除成功！')
        return redirect('event_management:event_type_list', project_id=project.id)
    
    return render(request, 'event_management/event_type_confirm_delete.html', {
        'project': project,
        'event_type': event_type,
    })

@login_required
@project_role_required(['admin'])
def argument_role_create(request, project_id, event_type_id):
    if request.method == 'POST':
        event_type = get_object_or_404(EventType, pk=event_type_id, project_id=project_id)
        try:
            role = ArgumentRole.objects.create(
                event_type=event_type,
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                is_required=request.POST.get('is_required') == 'on'
            )
            return JsonResponse({'status': 'success', 'role_id': role.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@login_required
@project_role_required(['admin'])
def argument_role_update(request, project_id, event_type_id, pk):
    if request.method == 'POST':
        role = get_object_or_404(ArgumentRole, pk=pk, event_type_id=event_type_id)
        try:
            role.name = request.POST.get('name')
            role.description = request.POST.get('description')
            role.is_required = request.POST.get('is_required') == 'on'
            role.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@login_required
@project_role_required(['admin'])
def argument_role_delete(request, project_id, event_type_id, pk):
    if request.method == 'POST':
        role = get_object_or_404(ArgumentRole, pk=pk, event_type_id=event_type_id)
        try:
            role.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})
