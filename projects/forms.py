from django import forms

from .models import Projects, Wiki, FileModel, Issues, IssuesType, Module, IssuesReply, ProjectInvite
from users.models import NewUser

import copy

class ProjectsForm(forms.ModelForm):

    class Meta:

        model = Projects
        fields = ['title', 'color', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "title",
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "项目描述",
                'rows': 3,
            }),
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_title(self):
        title = self.cleaned_data.get('title')
        queryset = Projects.objects.filter(by_user=self.request.user)
        exists = queryset.filter(title=title).exists()
        if exists:
            raise forms.ValidationError('您的项目中已包含当前项目') 
        
        if queryset.count() >= self.request.strategy.projects:
            raise forms.ValidationError('创建项目已达到最大数量，无法创建，请升级额度！') 
        
        return title
    
class ProjectsWikiForm(forms.ModelForm):

    class Meta:

        model = Wiki
        fields = ['title', 'content','parent']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "请输入文章标题",
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': "请输入文章内容",
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, request, *args, **kwargs):

        '''
        自定义下拉选择器的选项值
        让他的值匹配当前的项目ID
        '''

        super().__init__(*args, **kwargs)

        total_data_list = [('', '请选择'),]
        data = Wiki.objects.filter(project=request.project).values_list('id', 'title')
        total_data_list.extend(data)
        self.fields['parent'].choices = total_data_list


class FileForm(forms.ModelForm):

    class Meta:

        model = FileModel
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "请输入目录名称",
            })
        }

    def __init__(self, request, parent_object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.parent_object = parent_object

    def clean_name(self):
        name = self.cleaned_data.get('name')

        queryset = FileModel.objects.filter(file_type=2, name=name, project=self.request.project)

        if self.parent_object:
            exists = queryset.filter(parent=self.parent_object).exists()
        else:
            exists = queryset.filter(parent__isnull=True).exists()

        if exists:
            raise forms.ValidationError('当前目录中已存在该目录')
        
        return name

class FileUploadForm(forms.ModelForm):

    class Meta:

        model = FileModel
        fields = ['file_path']

class ProjectDeleteForm(forms.ModelForm):

    class Meta:

        model = Projects
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "请输入项目标题",
            })
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_title(self):

        title = self.cleaned_data.get('title')

        if title != self.request.project.title:
            raise forms.ValidationError('项目标题错误')
        
        if self.request.user != self.request.project.by_user:
            raise forms.ValidationError('只有项目创建者可以删除项目')
        
        return title
    
class BootStrapForm():

    bootstrap_class_exclude = []
    bootstrap_class_select = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.bootstrap_class_exclude:
                continue
            if name in self.bootstrap_class_select:
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = f'请输入{field.label}'

class IssuesForm(BootStrapForm, forms.ModelForm):

    bootstrap_class_exclude = [
        'assign', 
        'attention',
        'parent',
    ]
    bootstrap_class_select = [
        'issues_type', 
        'module', 
        'status', 
        'priority', 
        'mode',
    ]

    class Meta:

        model = Issues
        fields = [
            'issues_type',
            'subject',
            'module',
            'desc',
            'status',
            'priority',
            'assign',
            'attention',
            'start_date',
            'end_date',
            'mode',
            'parent',
        ]
        widgets = {
            'assign': forms.Select(attrs={
                'class': 'selectpicker',
                'data-live-search': "true"
            }),
            'parent': forms.Select(attrs={
                'class': 'selectpicker',
                'data-live-search': "true"
            }),
            'attention': forms.SelectMultiple(attrs={
                'class': 'selectpicker',
                'data-live-search': "true",
                'data-actions-box': "true",
            })
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 获取当前项目的所有问题类型
        self.fields['issues_type'].choices = IssuesType.objects.filter(project=request.project).values_list('id', 'title')

        # 获取当前项目所有模块
        self.fields['module'].choices = Module.objects.filter(project=request.project).values_list('id', 'title')
        
        # 获取当前项目的创建者和所有参与者
        total_data_list = [(request.project.by_user.id, request.project.by_user)]
        data = request.project.members.all().values_list('id', 'user_name')
        total_data_list.extend(data)
        self.fields['assign'].choices = [('', '没有选中任何项')] + total_data_list
        self.fields['attention'].choices = total_data_list

        # 获取当前项目的所有问题
        total_data_list = [('', '没有选中任何项')]
        data = Issues.objects.filter(project=request.project).values_list('id', 'subject')
        total_data_list.extend(data)
        self.fields['parent'].choices = total_data_list

class IssuesReplyForm(forms.ModelForm):

    class Meta:

        model = IssuesReply
        fields = ['content', 'parent']

class InviteForm(forms.ModelForm):
    ''' 项目邀请form '''
    class Meta:

        model = ProjectInvite
        fields = ['period', 'count']
        widgets = {
            'period': forms.Select(attrs={
                'class': 'form-select'
            }),
            'count': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }