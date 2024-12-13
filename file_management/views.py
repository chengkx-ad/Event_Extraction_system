from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from project_management.models import Project
from .models import Document, DocumentBatch
from .forms import DocumentForm, DocumentBatchForm, DocumentAssignForm
from project_management.decorators import project_role_required

@login_required
def document_list(request):
    # 获取用户所有的项目
    user_projects = request.user.projects.all()
    # 获取这些项目中的所有文档
    documents = Document.objects.filter(project__in=user_projects)
    return render(request, 'file_management/document_list.html', {
        'documents': documents,
        'projects': user_projects
    })

@login_required
@project_role_required(['admin', 'annotator'])
def document_upload(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.project = project
            document.uploaded_by = request.user
            
            # 处理文件上传
            uploaded_file = request.FILES['file']
            try:
                # 读取文件内容
                content = uploaded_file.read().decode('utf-8')
                document.content = content
                document.save()
                messages.success(request, '文档上传成功！')
                return redirect('file_management:document_list')
            except Exception as e:
                messages.error(request, f'文件处理失败：{str(e)}')
    else:
        form = DocumentForm()
    
    return render(request, 'file_management/document_form.html', {
        'form': form,
        'project': project,
    })

@login_required
def document_detail(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    document = get_object_or_404(Document, pk=pk, project=project)
    assign_form = DocumentAssignForm(project) if project.created_by == request.user else None
    
    context = {
        'project': project,
        'document': document,
        'assign_form': assign_form,
        'user': request.user,
    }
    return render(request, 'file_management/document_detail.html', context)

@login_required
def document_update(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    document = get_object_or_404(Document, pk=pk, project=project)
    if document.uploaded_by != request.user and project.created_by != request.user:
        messages.error(request, '您没有权限修改此文档！')
        return redirect('file_management:document_detail', project_id=project.id, pk=document.pk)
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=document)
        if form.is_valid():
            form.save()
            messages.success(request, '文档更新成功！')
            return redirect('file_management:document_detail', project_id=project.id, pk=document.pk)
    else:
        form = DocumentForm(instance=document)
    
    return render(request, 'file_management/document_form.html', {
        'form': form,
        'project': project,
        'document': document,
    })

@login_required
def document_delete(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    document = get_object_or_404(Document, pk=pk, project=project)
    if document.uploaded_by != request.user and project.created_by != request.user:
        messages.error(request, '您没有权限删除此文档！')
        return redirect('file_management:document_detail', project_id=project.id, pk=document.pk)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, '文档删除成功！')
        return redirect('file_management:document_list', project_id=project.id)
    
    return render(request, 'file_management/document_confirm_delete.html', {
        'project': project,
        'document': document,
    })

@login_required
def document_assign(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if project.created_by != request.user:
        messages.error(request, '只有项目创建者才能分配文档！')
        return redirect('file_management:document_detail', project_id=project.id, pk=pk)
    
    document = get_object_or_404(Document, pk=pk, project=project)
    
    if request.method == 'POST':
        form = DocumentAssignForm(project, request.POST)
        if form.is_valid():
            document.assigned_to = form.cleaned_data['annotator']
            document.status = 'processing'
            document.save()
            messages.success(request, '文档分配成功！')
    
    return redirect('file_management:document_detail', project_id=project.id, pk=pk)

# 批次管理视图
@login_required
def batch_list(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    batches = project.document_batches.all()
    context = {
        'project': project,
        'batches': batches,
    }
    return render(request, 'file_management/batch_list.html', context)

@login_required
def batch_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    if request.method == 'POST':
        form = DocumentBatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.project = project
            batch.save()
            messages.success(request, '批次创建成功！')
            return redirect('file_management:batch_detail', project_id=project.id, pk=batch.pk)
    else:
        form = DocumentBatchForm()
    
    return render(request, 'file_management/batch_form.html', {
        'form': form,
        'project': project,
    })

@login_required
def batch_detail(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    batch = get_object_or_404(DocumentBatch, pk=pk, project=project)
    available_documents = project.documents.exclude(batches=batch)
    
    context = {
        'project': project,
        'batch': batch,
        'available_documents': available_documents,
    }
    return render(request, 'file_management/batch_detail.html', context)

@login_required
def batch_update(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    batch = get_object_or_404(DocumentBatch, pk=pk, project=project)
    
    if request.method == 'POST':
        form = DocumentBatchForm(request.POST, instance=batch)
        if form.is_valid():
            form.save()
            messages.success(request, '批次更新成功！')
            return redirect('file_management:batch_detail', project_id=project.id, pk=batch.pk)
    else:
        form = DocumentBatchForm(instance=batch)
    
    return render(request, 'file_management/batch_form.html', {
        'form': form,
        'project': project,
        'batch': batch,
    })

@login_required
def batch_delete(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    batch = get_object_or_404(DocumentBatch, pk=pk, project=project)
    
    if request.method == 'POST':
        batch.delete()
        messages.success(request, '批次删除成功！')
        return redirect('file_management:batch_list', project_id=project.id)
    
    return render(request, 'file_management/batch_confirm_delete.html', {
        'project': project,
        'batch': batch,
    })

@login_required
def batch_add_documents(request, project_id, pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    batch = get_object_or_404(DocumentBatch, pk=pk, project=project)
    
    if request.method == 'POST':
        document_ids = request.POST.getlist('documents')
        documents = Document.objects.filter(id__in=document_ids, project=project)
        batch.documents.add(*documents)
        messages.success(request, '文档添加成功！')
    
    return redirect('file_management:batch_detail', project_id=project.id, pk=batch.pk)

@login_required
def batch_remove_document(request, project_id, pk, doc_pk):
    project = get_object_or_404(Project, pk=project_id)
    if not project.members.filter(id=request.user.id).exists():
        messages.error(request, '您没有权限访问此项目！')
        return redirect('project_management:project_list')
    
    batch = get_object_or_404(DocumentBatch, pk=pk, project=project)
    document = get_object_or_404(Document, pk=doc_pk, project=project)
    
    if request.method == 'POST':
        batch.documents.remove(document)
        messages.success(request, '文档移除成功！')
    
    return redirect('file_management:batch_detail', project_id=project.id, pk=batch.pk)
