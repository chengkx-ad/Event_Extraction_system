from django.db import models
from project_management.models import Project, User

class Document(models.Model):
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('reviewed', '已审核'),
    ]

    title = models.CharField('文档标题', max_length=200)
    content = models.TextField('文档内容')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents', verbose_name='所属项目')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='pending')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents', verbose_name='上传者')
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_documents', verbose_name='分配给')

    class Meta:
        verbose_name = '文档'
        verbose_name_plural = '文档'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
    
    def can_annotate(self, user):
        """检查用户是否可以标注此文档"""
        return self.assigned_to == user and self.status in ['pending', 'processing']
    
    def get_or_create_annotation(self, user):
        """获取或创建用户的标注"""
        from annotation.models import Annotation
        annotation = self.annotations.filter(annotator=user).first()
        if not annotation:
            annotation = Annotation.objects.create(
                document=self,
                annotator=user,
                status='draft'
            )
        return annotation

class DocumentBatch(models.Model):
    name = models.CharField('批次名称', max_length=100)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='document_batches', verbose_name='所属项目')
    documents = models.ManyToManyField(Document, related_name='batches', verbose_name='文档')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    description = models.TextField('描述', blank=True)

    class Meta:
        verbose_name = '文档批次'
        verbose_name_plural = '文档批次'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
