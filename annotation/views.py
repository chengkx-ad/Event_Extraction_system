from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from file_management.models import Document
from .models import Annotation, EventAnnotation, ArgumentAnnotation
from .forms import (
    AnnotationForm, EventAnnotationForm, ArgumentAnnotationForm, 
    AnnotationReviewForm
)
import logging
import json

logger = logging.getLogger(__name__)

@login_required
def annotation_task_list(request):
    # 获取分配给当前用户的待处理文档
    documents = Document.objects.filter(
        assigned_to=request.user,
        status__in=['pending', 'processing']
    ).order_by('uploaded_at')
    
    # 添加日志记录
    logger.debug(f"User: {request.user.username}, Documents: {documents}")
    
    context = {
        'documents': documents,
    }
    return render(request, 'annotation/task_list.html', context)

@login_required
def completed_task_list(request):
    # 获取当前用户已完成的标注任务
    annotations = Annotation.objects.filter(
        annotator=request.user,
        status__in=['submitted', 'reviewed', 'rejected']
    ).order_by('-updated_at')
    
    context = {
        'annotations': annotations,
    }
    return render(request, 'annotation/completed_task_list.html', context)

@login_required
def annotate_document(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    
    # 检查标注权限
    if not document.can_annotate(request.user):
        messages.error(request, '您没有权限标注此文档！')
        return redirect('annotation:task_list')
    
    # 获取或创建标注
    annotation = document.get_or_create_annotation(request.user)
    
    # 如果标注已提交或已审核，则不允许修改
    if annotation.status in ['submitted', 'reviewed']:
        messages.warning(request, '此文档的标注已提交或已审核，无法修改！')
        return redirect('annotation:task_list')
    
    # 更新文档状态
    if document.status == 'pending':
        document.status = 'processing'
        document.save()
    
    # 准备事件数据的JSON
    events_json = []
    for event in annotation.events.all():
        event_data = {
            'id': event.id,
            'text': event.text,
            'arguments': []
        }
        for argument in event.arguments.all():
            event_data['arguments'].append({
                'id': argument.id,
                'text': argument.text,
                'role': argument.role.name
            })
        events_json.append(event_data)
    
    context = {
        'document': document,
        'annotation': annotation,
        'event_form': EventAnnotationForm(document.project),
        'events_json': json.dumps(events_json)
    }
    return render(request, 'annotation/annotate_document.html', context)

@login_required
def submit_annotation(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    annotation = get_object_or_404(Annotation, document=document, annotator=request.user)
    
    if request.method == 'POST':
        # 检查是否有标注的事件
        if not annotation.events.exists():
            messages.error(request, '请至少标注一个事件后再提交！')
            return redirect('annotation:annotate_document', document_id=document.id)
        
        # 更新状态
        annotation.status = 'submitted'
        annotation.save()
        
        # 更新文档状态
        document.status = 'completed'
        document.save()
        
        messages.success(request, '标注提交成功！')
        return redirect('annotation:task_list')
    
    return redirect('annotation:annotate_document', document_id=document.id)

@login_required
def add_event(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    annotation = get_object_or_404(Annotation, document=document, annotator=request.user)
    
    if request.method == 'POST':
        form = EventAnnotationForm(document.project, request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.annotation = annotation
            event.save()
            return JsonResponse({
                'status': 'success',
                'event': {
                    'id': event.id,
                    'type': event.event_type.name,
                    'text': event.text,
                }
            })
        return JsonResponse({'status': 'error', 'errors': form.errors})
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@login_required
def update_event(request, document_id, event_id):
    document = get_object_or_404(Document, pk=document_id)
    event = get_object_or_404(EventAnnotation, pk=event_id, annotation__document=document)
    
    if request.method == 'POST':
        form = EventAnnotationForm(document.project, request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            return JsonResponse({
                'status': 'success',
                'event': {
                    'id': event.id,
                    'type': event.event_type.name,
                    'text': event.text,
                }
            })
        return JsonResponse({'status': 'error', 'errors': form.errors})
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@login_required
def delete_event(request, document_id, event_id):
    document = get_object_or_404(Document, pk=document_id)
    event = get_object_or_404(EventAnnotation, pk=event_id, annotation__document=document)
    
    if request.method == 'POST':
        event.delete()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@login_required
def add_argument(request, document_id, event_id):
    document = get_object_or_404(Document, pk=document_id)
    event = get_object_or_404(EventAnnotation, pk=event_id, annotation__document=document)
    
    if request.method == 'POST':
        form = ArgumentAnnotationForm(event.event_type, request.POST)
        if form.is_valid():
            argument = form.save(commit=False)
            argument.event = event
            argument.save()
            return JsonResponse({
                'status': 'success',
                'argument': {
                    'id': argument.id,
                    'role': argument.role.name,
                    'text': argument.text,
                }
            })
        return JsonResponse({'status': 'error', 'errors': form.errors})
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@login_required
def update_argument(request, document_id, event_id, argument_id):
    document = get_object_or_404(Document, pk=document_id)
    event = get_object_or_404(EventAnnotation, pk=event_id, annotation__document=document)
    argument = get_object_or_404(ArgumentAnnotation, pk=argument_id, event=event)
    
    if request.method == 'POST':
        form = ArgumentAnnotationForm(event.event_type, request.POST, instance=argument)
        if form.is_valid():
            argument = form.save()
            return JsonResponse({
                'status': 'success',
                'argument': {
                    'id': argument.id,
                    'role': argument.role.name,
                    'text': argument.text,
                }
            })
        return JsonResponse({'status': 'error', 'errors': form.errors})
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@login_required
def delete_argument(request, document_id, event_id, argument_id):
    document = get_object_or_404(Document, pk=document_id)
    event = get_object_or_404(EventAnnotation, pk=event_id, annotation__document=document)
    argument = get_object_or_404(ArgumentAnnotation, pk=argument_id, event=event)
    
    if request.method == 'POST':
        argument.delete()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': '不支持的请求方法'})

@login_required
def get_argument_form(request, document_id, event_id):
    document = get_object_or_404(Document, pk=document_id)
    event = get_object_or_404(EventAnnotation, pk=event_id, annotation__document=document)
    
    form = ArgumentAnnotationForm(event.event_type)
    return render(request, 'annotation/argument_form.html', {
        'form': form
    })

# 审核相关视图
@login_required
def review_list(request):
    # 获取需要审核的标注
    annotations = Annotation.objects.filter(
        Q(document__project__created_by=request.user) |  # 项目创建者
        Q(document__project__projectmembership__user=request.user,
          document__project__projectmembership__role='reviewer'),  # 审核者
        status='submitted'
    ).order_by('created_at')
    
    context = {
        'annotations': annotations,
    }
    return render(request, 'annotation/review_list.html', context)

@login_required
def review_annotation(request, annotation_id):
    annotation = get_object_or_404(Annotation, pk=annotation_id)
    
    # 检查权限
    if not (annotation.document.project.created_by == request.user or
            annotation.document.project.members.filter(
                projectmembership__user=request.user,
                projectmembership__role='reviewer'
            ).exists()):
        messages.error(request, '您没有权限审核此标注！')
        return redirect('annotation:review_list')
    
    review_form = AnnotationReviewForm(instance=annotation)
    
    context = {
        'annotation': annotation,
        'review_form': review_form,
    }
    return render(request, 'annotation/review_annotation.html', context)

@login_required
def submit_review(request, annotation_id):
    annotation = get_object_or_404(Annotation, pk=annotation_id)
    
    if request.method == 'POST':
        form = AnnotationReviewForm(request.POST, instance=annotation)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewed_by = request.user
            review.save()
            
            messages.success(request, '审核意见提交成功！')
            return redirect('annotation:review_list')
        
        messages.error(request, '表单验证失败，请检查输入！')
    
    return redirect('annotation:review_annotation', annotation_id=annotation.id)
