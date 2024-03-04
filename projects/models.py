from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Projects(models.Model):
    '''
    项目模型
    '''
    title = models.CharField(_('项目标题'), max_length=200)
    description = models.TextField(_('项目描述'), max_length=500)
    color = models.CharField(_('颜色'), max_length=20, default='#ffffff')
    is_markers = models.BooleanField(_('是否星标'), default=False)
    member_num = models.PositiveIntegerField(_('参与人数'))
    by_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='project', on_delete=models.CASCADE, verbose_name=_('创建者'))
    space = models.PositiveIntegerField(_('已使用空间'))
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='member_pro', through='Membership', through_fields=('project','person'))
    start_date = models.DateTimeField(_('创建时间'), auto_now_add=True)

    def __str__(self) -> str:
        return self.title
    
class Membership(models.Model):
    '''
    项目参与者模型
    '''
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership_p')
    is_markers = models.BooleanField(_('是否星标'), default=False)
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='membership_i', default=1)
    create_date = models.DateTimeField(_('创建时间'), auto_now_add=True)

class Wiki(models.Model):
    '''
    wiki模型
    '''
    title = models.CharField(_('文章标题'), max_length=200)
    content = models.TextField(_('文章内容'), max_length=2000)
    project = models.ForeignKey(Projects, related_name='wiki', on_delete=models.CASCADE)
    parent = models.ForeignKey(to='Wiki', related_name='child', on_delete=models.CASCADE, null=True, blank=True)
    depth = models.IntegerField(_('深度'), default=1)
    create_date = models.DateTimeField(_('创建时间'), auto_now_add=True)

    def __str__(self):
        return self.title
    
class FileModel(models.Model):
    '''
    文件模型
    '''
    name = models.CharField(_('名称'), max_length=120)
    file_type = models.SmallIntegerField(_('文件类型'), choices=((1, '文件'), (2, '文件夹')))
    size = models.PositiveIntegerField(_('大小'), null=True, blank=True)
    parent = models.ForeignKey(to='FileModel', related_name='child', on_delete=models.CASCADE, null=True, blank=True)
    key = models.CharField(_('Key名称'), max_length=120, null=True, blank=True)
    file_path = models.FileField(_('路径'), max_length=255, upload_to='file/', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='up_user', on_delete=models.CASCADE)
    update_date = models.DateTimeField(_('更新时间'), auto_now=True)
    project = models.ForeignKey(Projects, related_name='file', on_delete=models.CASCADE)


class Module(models.Model):
    '''
    模块（里程碑）
    '''
    PROJECT_INIT_LIST = ['注册', '登录', '退出']

    title = models.CharField(_('模块名称'), max_length=32)
    project = models.ForeignKey(Projects, related_name='module', on_delete=models.CASCADE, verbose_name='项目')
    
    def __str__(self):
        return self.title
    
class IssuesType(models.Model):
    '''
    问题类型,例如:任务,功能,Bug
    '''
    PROJECT_INIT_LIST = ['任务', '功能', 'Bug']

    title = models.CharField(_('类型名称'), max_length=32)
    project = models.ForeignKey(Projects, related_name='issuestype', on_delete=models.CASCADE, verbose_name='项目')

    def __str__(self):
        return self.title
    
class Issues(models.Model):
    '''
    问题
    '''
    project = models.ForeignKey(Projects, related_name='issues', on_delete=models.CASCADE, verbose_name='项目')
    issues_type = models.ForeignKey(IssuesType, related_name='issues', on_delete=models.CASCADE, verbose_name='问题类型')
    module = models.ForeignKey(Module, related_name='issues', on_delete=models.CASCADE, verbose_name='模块')

    subject = models.CharField(_('主题'), max_length=80)
    desc = models.TextField(_('问题描述'))
    priority_choices = (
        ('danger', '高'),
        ('warning', '中'),
        ('success', '低'),
    )
    priority = models.CharField(_('优先级'), max_length=12, choices=priority_choices, default='danger')

    status_choices = (
        (1, '新建'),
        (2, '处理中'),
        (3, '已解决'),
        (4, '已忽略'),
        (5, '待反馈'),
        (6, '已关闭'),
        (7, '重新打开'),
    )
    status = models.SmallIntegerField(_('状态'), choices=status_choices, default=1)

    assign = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='task', on_delete=models.CASCADE, verbose_name='指派', null=True, blank=True)
    attention = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='observe', verbose_name='关注者', blank=True)
    start_date = models.DateField(_('开始时间'), null=True, blank=True)
    end_date = models.DateField(_('结束时间'), null=True, blank=True)

    mode_choices = (
        (1, '公开模式'),
        (2, '隐私模式'),
    )
    mode = models.SmallIntegerField(_('模式'), choices=mode_choices, default=1)

    parent = models.ForeignKey('self', related_name='child', on_delete=models.SET_NULL, verbose_name='父问题', null=True, blank=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='create_problems', on_delete=models.CASCADE, verbose_name='创建者')
    create_datetiem = models.DateTimeField(_('创建时间'), auto_now_add=True)
    latest_update_datetiem = models.DateTimeField(_('最后更新时间'), auto_now=True)

    def __str__(self):
        return self.subject
    
class IssuesReply(models.Model):
    '''
        问题回复
    '''
    reply_type_choices = (
        (1, '修改记录'),
        (2, '回复'),
    )
    reply_type = models.SmallIntegerField(_('类型'), choices=reply_type_choices)

    issues = models.ForeignKey(Issues, related_name='i_reply', on_delete=models.CASCADE, verbose_name='问题')
    content = models.TextField(_('描述'))
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='creator_reply', on_delete=models.CASCADE, verbose_name='创建者')
    create_datetiem = models.DateTimeField(_('创建时间'), auto_now_add=True)
    parent = models.ForeignKey('self', related_name='parent_reply', on_delete=models.SET_NULL, verbose_name='父回复', null=True, blank=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver_reply', on_delete=models.SET_NULL, verbose_name='接收者', null=True, blank=True)

class ProjectInvite(models.Model):
    ''' 项目邀请码 '''
    project = models.ForeignKey(Projects, related_name='projectinvite', on_delete=models.CASCADE, verbose_name='项目')
    code = models.CharField(_('邀请码'), max_length=64, unique=True)
    count = models.PositiveIntegerField(_('限制数量'), null=True, blank=True, help_text='空表示无数量限制')
    use_count = models.PositiveIntegerField(_('已邀请数量'), default=0)
    period_choices = (
        (30, '30分钟'),
        (60, '1小时'),
        (300, '5小时'),
        (1440, '24小时'),
    )
    period = models.IntegerField(_('有效期'), choices=period_choices, default=1440)
    create_datetiem = models.DateTimeField(_('创建时间'), auto_now_add=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='creator_invite', on_delete=models.CASCADE, verbose_name='创建者')
