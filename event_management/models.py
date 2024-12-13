from django.db import models
from project_management.models import Project

class EventType(models.Model):
    name = models.CharField('事件类型名称', max_length=100)
    description = models.TextField('描述', blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='event_types', verbose_name='所属项目')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '事件类型'
        verbose_name_plural = '事件类型'
        unique_together = ['name', 'project']

    def __str__(self):
        return self.name

class ArgumentRole(models.Model):
    name = models.CharField('论元角色名称', max_length=100)
    description = models.TextField('描述', blank=True)
    event_type = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name='argument_roles', verbose_name='事件类型')
    is_required = models.BooleanField('是否必需', default=False)

    class Meta:
        verbose_name = '论元角色'
        verbose_name_plural = '论元角色'
        unique_together = ['name', 'event_type']

    def __str__(self):
        return f"{self.event_type.name}-{self.name}"
