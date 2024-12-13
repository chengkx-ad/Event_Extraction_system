from django.db import models
from django.contrib.auth.models import User
from file_management.models import Document
from event_management.models import EventType, ArgumentRole

class Annotation(models.Model):
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('submitted', '已提交'),
        ('reviewed', '已审核'),
        ('rejected', '已驳回'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='annotations', verbose_name='文档')
    annotator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='annotations', verbose_name='标注者')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_annotations', verbose_name='审核者')
    review_comment = models.TextField('审核意见', blank=True)

    class Meta:
        verbose_name = '标注'
        verbose_name_plural = '标注'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.document.title}-{self.annotator.username}"

class EventAnnotation(models.Model):
    annotation = models.ForeignKey(Annotation, on_delete=models.CASCADE, related_name='events', verbose_name='标注')
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, verbose_name='事件类型')
    start_offset = models.IntegerField('开始位置')
    end_offset = models.IntegerField('结束位置')
    text = models.CharField('事件文本', max_length=500)

    class Meta:
        verbose_name = '事件标注'
        verbose_name_plural = '事件标注'

    def __str__(self):
        return f"{self.event_type.name}-{self.text}"

class ArgumentAnnotation(models.Model):
    event = models.ForeignKey(EventAnnotation, on_delete=models.CASCADE, related_name='arguments', verbose_name='事件')
    role = models.ForeignKey(ArgumentRole, on_delete=models.CASCADE, verbose_name='论元角色')
    start_offset = models.IntegerField('开始位置')
    end_offset = models.IntegerField('结束位置')
    text = models.CharField('论元文本', max_length=500)

    class Meta:
        verbose_name = '论元标注'
        verbose_name_plural = '论元标注'

    def __str__(self):
        return f"{self.role.name}-{self.text}"
