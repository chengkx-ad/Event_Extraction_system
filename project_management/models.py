from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField('项目名称', max_length=100)
    description = models.TextField('项目描述', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects', verbose_name='创建者')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)
    members = models.ManyToManyField(User, through='ProjectMembership', related_name='projects')

    class Meta:
        verbose_name = '项目'
        verbose_name_plural = '项目'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class ProjectMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', '管理员'),
        ('annotator', '标注者'),
        ('reviewer', '审核者'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField('加入时间', auto_now_add=True)

    class Meta:
        verbose_name = '项目成员'
        verbose_name_plural = '项目成员'
        unique_together = ['project', 'user']
