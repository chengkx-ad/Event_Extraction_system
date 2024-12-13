from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, ProjectMembership
from .forms import ProjectForm, ProjectMembershipForm, UserRegistrationForm
from .decorators import project_role_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def project_list(request):
    created_projects = Project.objects.filter(created_by=request.user)
    user_projects = request.user.projects.all()
    return render(request, 'project_management/project_list.html', {
        'created_projects': created_projects,
        'user_projects': user_projects
    })

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            ProjectMembership.objects.create(
                project=project,
                user=request.user,
                role='admin'
            )
            messages.success(request, '项目创建成功')
            return redirect('project_management:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'project_management/project_form.html', {'form': form})

@login_required
@project_role_required(['admin', 'annotator', 'reviewer'])
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user_role = project.projectmembership_set.get(user=request.user).role
    
    # 预处理��据
    stats = {
        'member_count': project.members.count(),
        'document_count': project.documents.count(),
        'event_type_count': project.event_types.count(),
        'completed_count': project.documents.filter(status='completed').count(),
    }
    
    return render(request, 'project_management/project_detail.html', {
        'project': project,
        'user_role': user_role,
        'stats': stats,
    })

@login_required
@project_role_required(['admin'])
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, '项目更新成功')
            return redirect('project_management:project_detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(request, 'project_management/project_form.html', {
        'form': form,
        'project': project
    })

@login_required
@project_role_required(['admin'])
def add_member(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectMembershipForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']
            if ProjectMembership.objects.filter(project=project, user=user).exists():
                messages.error(request, '该用户已是项目成员')
            else:
                membership = form.save(commit=False)
                membership.project = project
                membership.user = user
                membership.role = role
                membership.save()
                messages.success(request, '成员添加成功')
            return redirect('project_management:project_detail', pk=project.pk)
    else:
        form = ProjectMembershipForm()
    return render(request, 'project_management/member_form.html', {
        'form': form,
        'project': project
    })

@login_required
@project_role_required(['admin'])
def remove_member(request, pk, member_pk):
    project = get_object_or_404(Project, pk=pk)
    membership = get_object_or_404(ProjectMembership, pk=member_pk, project=project)
    if membership.user != project.created_by:
        membership.delete()
        messages.success(request, '成员移除成功')
    else:
        messages.error(request, '不能移除项目创建者')
    return redirect('project_management:project_detail', pk=project.pk)

@login_required
@project_role_required(['admin'])
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, '注册成功，请登录。')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'project_management/register.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # 更新会话，防止密码修改后被登出
            update_session_auth_hash(request, user)
            messages.success(request, '密码修改成功！')
            return redirect('project_management:project_list')
        else:
            messages.error(request, '请修正下面的错误。')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'project_management/change_password.html', {
        'form': form
    })
