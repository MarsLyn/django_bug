from django.db import models
from django.utils.translation import gettext_lazy as _


class Strategy(models.Model):

    title = models.CharField(_('标题'), max_length=200)
    s_type = models.SmallIntegerField(_('分类'), choices=((1, '免费'), (2, '收费'), (3, '其他')), default=1)
    price = models.DecimalField(_('价格/年'), max_digits=5, decimal_places=2)
    projects = models.PositiveIntegerField(_('创建项目最大数量'))
    member = models.PositiveIntegerField(_('项目成员最大数量'))
    space = models.PositiveIntegerField(_('项目最大使用空间'))
    uploda = models.PositiveIntegerField(_('文件最大上传大小'))
    start_date = models.DateTimeField(_('创建时间'), auto_now_add=True)

    def __str__(self) -> str:
        return self.title