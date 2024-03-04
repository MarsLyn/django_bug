from typing import Any
from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.base import View, TemplateResponseMixin, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, ModelFormMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import F
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.db.models import Count, Avg
from django_redis import get_redis_connection

import json
import copy
import hashlib
import uuid
import datetime
import time

from .models import (
    Projects, 
    Membership, 
    Wiki, 
    FileModel, 
    Issues, 
    IssuesType, 
    Module, 
    IssuesReply,
    ProjectInvite,
)
from .forms import (
    ProjectsForm, 
    ProjectsWikiForm, 
    FileForm, 
    FileUploadForm, 
    ProjectDeleteForm, 
    IssuesForm,
    IssuesReplyForm,
    InviteForm,
)

from goods.models import Goods
from strategy.models import Strategy

class CreateRandom():

    def md5(self, string):
        hashlib_object = hashlib.md5(settings.SECRET_KEY.encode('utf-8'))
        hashlib_object.update(string.encode('utf-8'))
        return hashlib_object.hexdigest()

    def uid(self, string):
        data = f'{str(uuid.uuid4())}-{string}'
        return self.md5(data)

class ProjectsListView(LoginRequiredMixin, ListView):
    ''' 项目列表 '''

    login_url = reverse_lazy('user:login_smscod')
    template_name = 'projects/projects_list.html'
    queryset = Projects.objects.all()

    def get_queryset(self):
        # print(self.request.strategy)
        self.queryset = super().get_queryset()
        self.queryset = self.queryset.filter(by_user=self.request.user)
        self.membership = Membership.objects.filter(person=self.request.user)
        return self.queryset
    
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        context['form'] = ProjectsForm(self.request)

        project_dict = {'star': [], 'my': [], 'join': []}

        for row in self.queryset:
            if row.is_markers:
                project_dict['star'].append({'data': row, 'type': 'my'})
            else:
                project_dict['my'].append(row)

        for row in self.membership:
            if row.is_markers:
                project_dict['star'].append({'data': row.project, 'type': 'join'})
            else:
                project_dict['join'].append(row.project)

        context['object_list'] = project_dict

        return context
    
class ProjectsCreateView(LoginRequiredMixin, CreateView):
    ''' 项目创建 '''

    login_url = reverse_lazy('user:login_smscod')
    form_class = ProjectsForm
    success_url = reverse_lazy('projects:list')

    def form_valid(self, form):
        self.object = Projects(**form.cleaned_data)
        self.object.member_num = 1
        self.object.by_user = self.request.user
        self.object.space = 0
        self.object.save()

        # 创建项目时初始化创建问题类型
        issuestype_object_list = []
        for item in IssuesType.PROJECT_INIT_LIST:
            issuestype_object_list.append(IssuesType(title=item, project=self.object))
        IssuesType.objects.bulk_create(issuestype_object_list)

        # 创建项目时初始化创建问题模块
        module_object_list = []
        for item in Module.PROJECT_INIT_LIST:
            module_object_list.append(Module(title=item, project=self.object))
        Module.objects.bulk_create(module_object_list)

        return JsonResponse({'status': True, 'message': '添加成功'})
    
    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'status': False, 'message': errors})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs
    
class ProjectsDashboardView(DetailView):
    ''' 项目概览 '''

    template_name = 'projects/dashboard.html'
    queryset = Projects.objects.all()

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context_dict = {}

        # 获取当前项目的问题状态数量
        status_dict = {}
        for key, value in Issues.status_choices:
            status_dict[key] = {'text': value, 'num': 0}

        status_queryset = Issues.objects.filter(project=self.request.project).values('status').annotate(num_status=Count('status'))
        for item in status_queryset:
            status_dict[item['status']]['num'] = item['num_status']

        # 获取当前项目的参与者
        person_queryset = Membership.objects.filter(project=self.request.project).values('person__user_name')
        # print(person_queryset)

        # 获取当前项目问题动态的前十个指派操作
        top_ten_queryset = Issues.objects.filter(
            project=self.request.project,
            assign__isnull=False
        ).order_by('-create_datetiem').values(
            'id', 
            'creator__user_name',
            'assign__user_name',
            'create_datetiem',
        )[:10]
        # print(top_ten_queryset)

        context_dict['status_dict'] = status_dict
        context_dict['membership_list'] = person_queryset
        context_dict['top_ten_list'] = top_ten_queryset

        context = self.get_context_data(object=self.object, **context_dict)
        # print(context)

        return self.render_to_response(context)
    
class DashboardIssuesChartView(View):
    ''' 项目概览里面的问题新增趋势 '''

    def get(self, request, *args, **kwargs):

        # 获取最近30天，每天创建的问题数量。

        # 1. 生成30天的日期
        date_dict = {}
        date_now = datetime.datetime.now().date()
        for item in range(30):
            # print(date_now)
            date = date_now - datetime.timedelta(days=item)
            date_dict[date.strftime('%Y-%m-%d')] = [time.mktime(date.timetuple()) * 1000, 0]

        # print(date_dict)

        # 2. 获取最近30天，每天创建的问题数量。
        result = Issues.objects.filter(
            project=request.project, 
            create_datetiem__date__gte=date_now - datetime.timedelta(days=30)
        ).values('create_datetiem__date').annotate(num=Count('id'))

        # print(result)

        # 3. 把每天的数量赋到date_dict中
        for item in result:
            date_dict[item['create_datetiem__date'].strftime('%Y-%m-%d')][1] = item['num']

        # print(list(date_dict.values()))

        data_list = list(date_dict.values())

        return JsonResponse({'status': True, 'data': data_list})
    
class ProjectsIssuesListView(ModelFormMixin, ListView):
    ''' 问题的列表页 '''

    template_name = 'projects/issues_list.html'
    queryset = Issues.objects.all()
    form_class = IssuesForm
    paginate_by = 5
    allow_filter_name = ['status', 'priority', 'issues_type', 'assign', 'attention', ] # 筛选的字段
    ordering = 'id'

    def get(self, request, *args, **kwargs):
        self.object = None
        self.get_filter()
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def get_filter(self):
        # 获取并返回筛选的条件
        condition = {} # 用于字段筛选的条件
        for name in self.allow_filter_name:
            value_list = self.request.GET.getlist(name)
            if not value_list:
                continue
            condition[f'{name}__in'] = value_list
        return condition
    
    def get_filter_html(self, name, data_list, type='checked'):
        # 生成筛选条件的URL，text，checked
        get_list = self.request.GET.getlist(name)

        for item in data_list:
            url = ''
            url_list = copy.deepcopy(get_list)
            text = item[1]
            checked = ''
            # 如果当前用户请求的URL中和当前循环的URL相等
            if str(item[0]) in get_list:
                if type == 'select':
                    checked = 'selected'
                else:
                    checked = 'checked'
                url_list.remove(str(item[0]))
            else:
                url_list.append(str(item[0]))

            query_dict = self.request.GET.copy()
            # print(query_dict)
            query_dict.setlist(name, url_list)
            # print(query_dict)

            if query_dict.get('page'):
                query_dict.setlist('page', ['1',])

            url = f'?{query_dict.urlencode()}'

            if url == '?':
                url = self.request.path_info

            # print(url)
            yield {'url': url, 'text': text, 'checked':checked}

    def get_queryset(self, query=None):
        condition = self.get_filter()
        ordering = self.get_ordering()
        query_set = self.queryset.filter(project=self.request.project)

        if condition:
            query_set = query_set.filter(**condition)

        # print(condition)
        # print(query_set)

        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            query_set = query_set.order_by(*ordering)

        return query_set
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self):

        # 获取项目的创建者和参与者
        default_list = [(self.request.project.by_user.id, self.request.project.by_user)]
        default_list.extend(self.request.project.members.all().values_list('id', 'user_name'))

        context = super().get_context_data()

        context['status_filter'] = self.get_filter_html('status', Issues.status_choices)
        context['priority_filter'] = self.get_filter_html('priority', Issues.priority_choices)
        context['issues_type_filter'] = self.get_filter_html('issues_type', IssuesType.objects.filter(project=self.request.project).values_list('id', 'title'))
        context['assign_filter'] = self.get_filter_html('assign', default_list, type='select')
        context['attention_filter'] = self.get_filter_html('attention', default_list, type='select')
        context['invite_form'] = InviteForm()

        return context
        
    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.project = self.request.project
        form.save()
        return JsonResponse({'status': True, 'message': ''})
    
    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'status': False, 'message': errors})
    
class InviteCodeCreateView(CreateRandom, CreateView):
    ''' 创建邀请码 '''

    form_class = InviteForm

    def form_valid(self, form):
        '''
        1. 创建随机的邀请码
        2. 邀请码保存到数据库
        3. 限制只有创建者才能邀请
        '''
        if self.request.user != self.request.project.by_user:
            form.add_error('period', '只有当前项目的创建者才能邀请')
            return self.form_invalid(form)
        
        # 生成随机邀请码字符串
        random_invite_code = self.uid(self.request.user.email)

        # 把邀请码保存到数据库
        form.instance.project = self.request.project
        form.instance.code = random_invite_code
        form.instance.creator = self.request.user
        form.save()

        # 生成邀请码的链接返回给前端
        url = f'{self.request.scheme}://{self.request.get_host()}{reverse("projects:invite_join", kwargs={"code": random_invite_code})}'

        return JsonResponse({'status': True, 'data': url})


    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'status': False, 'message': errors})
    
class InviteJoinView(LoginRequiredMixin, TemplateView):
    ''' 访问邀请码 '''
    
    template_name = 'projects/invite_join.html'
    login_url = reverse_lazy('user:login_smscod')

    def get(self, request, *args, **kwargs):

        context = self.get_context_data(**kwargs)

        invite_obj = ProjectInvite.objects.filter(code=kwargs.get('code')).first()

        '''
        1. 判断邀请码是否存在
        2. 判断是否是创建者访问邀请码
        3. 判断是否是项目已参与人员访问邀请码
        4. 判断项目成员是否超限
        5. 判断邀请码是否过期
        6. 判断邀请码数量是否用完
        '''

        if not invite_obj:
            context['error'] = '邀请码不存在'
            return self.render_to_response(context)
        
        # 获取当前时间
        current_datetime = datetime.datetime.now()
        if current_datetime > invite_obj.create_datetiem + datetime.timedelta(minutes=invite_obj.period):
            context['error'] = '邀请码已过期'
            return self.render_to_response(context)
        
        if invite_obj.count: # 当前邀请码的使用次数上限存在
            if invite_obj.use_count >= invite_obj.count: # 当前邀请码的使用次数大于使用次数上限
                context['error'] = '邀请码数量已使用完，无法加入项目'
                return self.render_to_response(context)

        if request.user == invite_obj.project.by_user:
            context['error'] = '创建者无需再加入项目'
            return self.render_to_response(context)
        
        exists = Membership.objects.filter(project=invite_obj.project, person=request.user).exists()
        if exists:
            context['error'] = '已加入项目无需再加入'
            return self.render_to_response(context)
        
        # 获取项目创建者的消费记录
        good_obj = Goods.objects.filter(by_user=invite_obj.project.by_user).order_by('-pk').first()
        if good_obj.end_date and good_obj.end_date < datetime.datetime.now(): # 已消费并且记录没有过期
            max_member = good_obj.strategy.member # 获取记录的最大上限人数
        else: # 未消费或记录已过期
            strategy_obj = Strategy.objects.get(pk=1)
            max_member = strategy_obj.member# 最大上限人数设置为免费上限

        # 获取项目目前参与的人数
        current_member = invite_obj.project.member_num

        if current_member == max_member: # 参与的人数等于最大上限人数
            context['error'] = '项目成员已经超限，无法加入项目'
            return self.render_to_response(context)
            
        # 把当前请求用户加入到项目中
        Membership.objects.create(
            project=invite_obj.project, 
            person=request.user, 
            invitee=invite_obj.project.by_user, 
        )

        # 邀请码使用次数加1
        invite_obj.use_count = F('use_count') + 1
        invite_obj.save()

        # 项目参与人数加1
        invite_obj.project.member_num = F('member_num') + 1
        invite_obj.project.save()
        context['invite_obj'] = invite_obj
        return self.render_to_response(context)

class IssuesDeatilView(ModelFormMixin, DetailView):
    ''' 问题的详情页面 '''

    template_name = 'projects/issues_detail.html'
    queryset = Issues.objects.all()
    form_class = IssuesForm
    pk_url_kwarg = 'issues_id'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # print(context)
        context['form'] = self.get_form()
        context['reply_object_list'] = IssuesReply.objects.filter(issues=self.object, issues__project=self.request.project)
        return context
    
class IssuesUpdateView(View):
    ''' 问题更新 '''

    def post(self, request, *args, **kwargs):

        post_dict = json.loads(request.body)
        print(post_dict)

        name = post_dict.get('name')
        value = post_dict.get('value')
        issues_obj = Issues.objects.filter(project=request.project, id=self.kwargs.get('issues_id')).first()
        field_obj = Issues._meta.get_field(name)

        # 1.数据库字段更新
        # 1.1 文本
        if name in ['subject', 'desc', 'start_date', 'end_date', ]:
            if not value: # 提交的数据为空
                if not field_obj.null:
                    return JsonResponse({'status': False, 'message': '您选择的值不能为空'})
                setattr(issues_obj, name, None)
                change_record = f'{field_obj.verbose_name}更新为空'
            else:
                setattr(issues_obj, name, value)
                change_record = f'{field_obj.verbose_name}更新为{value}'
            
            # 更新字段
            issues_obj.save()

            # 添加记录到操作记录表中
            IssuesReply.objects.create(
                reply_type = 1,
                issues = issues_obj,
                content = change_record,
                creator = request.user,
            )

            return JsonResponse({'status': True})
        # 1.2 FK
        if name in ['issues_type', 'module', 'assign', 'parent', ]:
            if not value: # 提交的数据为空
                if not field_obj.null: # 字段不允许为空
                    return JsonResponse({'status': False, 'message': '您选择的值不能为空'})
                
                setattr(issues_obj, name, None)
                change_record = f'{field_obj.verbose_name}更新为空'

            else: # 提交的数据不为空
                if name == 'assign': # 字段是指派者

                    if int(value) == request.project.by_user_id: # 指派者是项目创建者
                        instance = request.project.by_user
                    else: # 指派者是项目参与者
                        membership_obj = Membership.objects.filter(project=request.project, person_id=value).first()

                        if membership_obj: #参与者存在
                            instance = membership_obj.person
                        else:
                            instance = None

                    if not instance: # 指派者不存在
                        return JsonResponse({'status': False, 'message': '您选择的值不存在'})
                    
                    setattr(issues_obj, name, instance)
                    change_record = f'{field_obj.verbose_name}更新为{instance}'
                
                elif name == 'parent': # 字段是父问题

                    instance = Issues.objects.filter(project=request.project, id=value).first()

                    if not instance:
                        return JsonResponse({'status': False, 'message': '您选择的值不存在'})
                    
                    setattr(issues_obj, name, instance)
                    change_record = f'{field_obj.verbose_name}更新为{instance}'

                else:

                    # 查找表中是否存在这个数据
                    instance = field_obj.related_model.objects.filter(id=value, project=self.request.project).first()

                    if not instance: # 数据不存在
                        return JsonResponse({'status': False, 'message': '您选择的值不存在'})
                    
                    setattr(issues_obj, name, instance)
                    change_record = f'{field_obj.verbose_name}更新为{instance}'

            issues_obj.save()
            IssuesReply.objects.create(
                reply_type = 1,
                issues = issues_obj,
                content = change_record,
                creator = request.user,
            )
            return JsonResponse({'status': True})
        # 1.3 choices
        if name in ['status', 'priority', 'mode', ]:

            select_text = None

            if not value: # 提交的数据为空

                if not field_obj.null: # 字段不允许为空
                    return JsonResponse({'status': False, 'message': '您选择的值不能为空'})

                setattr(issues_obj, name, None)
                change_record = f'{field_obj.verbose_name}更新为空'

            else:

                for key, text in field_obj.choices:
                    if value == str(key): # 提交的choices存在
                        # 把文本传给select_text
                        select_text = text
                        break

                if not select_text: # select_text不存在
                    return JsonResponse({'status': False, 'message': '您选择的值不存在'})
                
                setattr(issues_obj, name, key)
                change_record = f'{field_obj.verbose_name}更新为{select_text}'

            issues_obj.save()

            IssuesReply.objects.create(
                reply_type = 1,
                issues = issues_obj,
                content = change_record,
                creator = request.user,
            )

            return JsonResponse({'status': True})
        # 1.4 M2M
        if name in ['attention', ]:

            if not isinstance(value, list):
                    return JsonResponse({'status': False, 'message': '数据格式错误'})

            if not value: # 提交的数据为空

                if not field_obj.null: # 字段不允许为空
                    return JsonResponse({'status': False, 'message': '您选择的值不能为空'})

                issues_obj.attention.set([])
                change_record = f'{field_obj.verbose_name}更新为空'
            
            else:
                # 查找项目的创建者和所有参与者
                # value = ['1', '2', '3']
                user_dict = {str(request.project.by_user.id): request.project.by_user.user_name}
                project_user_list = Membership.objects.filter(project=request.project)

                for item in project_user_list:
                    user_dict[str(item.person.id)] = item.person.user_name

                user_name_list = []
                for user_id in value:
                    user_name = user_dict.get(str(user_id))
                    if not user_name:
                        return JsonResponse({'status': False, 'message': '您选择的值不存在'})
                    user_name_list.append(user_name)

                issues_obj.attention.set(value)
                change_record = f'{field_obj.verbose_name}更新为空{','.join(user_name_list)}'

            issues_obj.save()

            IssuesReply.objects.create(
                reply_type = 1,
                issues = issues_obj,
                content = change_record,
                creator = request.user,
            )

            return JsonResponse({'status': True})

        return JsonResponse({'status': False, 'message': '滚！'})
    
class IssuesReplyView(ModelFormMixin, View):
    ''' 问题回复 '''

    form_class = IssuesReplyForm
    queryset = IssuesReply.objects.all()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form):
        # print(form.cleaned_data)
        parent = form.cleaned_data.get('parent')
        if parent:
            form.instance.receiver = parent.creator
        form.instance.reply_type = 2
        form.instance.issues_id = self.kwargs.get('issues_id')
        form.instance.creator = self.request.user
        form.save()
        return JsonResponse({'status': True})
    
    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'status': False, 'message': errors})

class ProjectsStatisticsView(TemplateView):
    ''' 项目统计 '''

    template_name = 'projects/statistics.html'
    
class StatisticsPriorityView(View):
    ''' 优先级统计 '''

    def get(self, request, *args, **kwargs):
        # 更具提交的初始化日期和结束日期获取每个优先级的问题数量

        start = request.GET.get('start')
        end = request.GET.get('end')

        # 1. 构造每个优先级初始值
        priority_dict = {}
        for key, value in Issues.priority_choices:
            priority_dict[key] = {'name': value, 'y': 0}
        # print(priority_dict)

        # 2. 根据日期查找每个优先级的问题数量
        issues_queryset = Issues.objects.filter(
            project=request.project, 
            create_datetiem__date__range=(start, end)
        ).values('priority').annotate(num=Count('id'))
        # print(issues_queryset.query)

        # 3. 根据获取到的每个优先级数量来修改初始值
        for item in issues_queryset:
            priority_dict[item['priority']]['y'] = item['num']
            
        data = priority_dict
        
        return JsonResponse({"status": True, 'data': list(data.values())})
    
class StatisticsUserView(View):
    ''' 人员工作进度 '''

    def get(self, request, *args, **kwargs):
        # 根据提交的日期获取当前项目每个指派人员的问题数量，然后在根据问题的每个状态获取指派的数量

        start = request.GET.get('start')
        end = request.GET.get('end')

        issues_queryset = request.project.issues.filter(
            create_datetiem__date__range=(start, end)
        )
        # print(issues_queryset.query)
        # for item in issues_queryset:
        #     print(item)

        user_dict = {
            request.project.by_user.id: request.project.by_user.user_name,
        }

        members_queryset = request.project.members.all()
        for item in members_queryset:
            user_dict[item.id] = item.user_name

        user_dict[None] = '未指派'

        status_dict = {
            # 1: {
            #     'name': '新建',
            #     'data': [3, 5, 1, 13]
            # }
        }
        for key, value in Issues.status_choices:
            status_dict[key] = {'name': value, 'data': [ 0 for i in range(len(user_dict)) ]}

        index = 0
        for key in user_dict.keys():
            if key:
                issues_count = issues_queryset.filter(assign_id=key).values('status').annotate(num=Count('id'))
            else:
                issues_count = issues_queryset.filter(assign__isnull=True).values('status').annotate(num=Count('id'))
            
            for item in issues_count:
                status_dict[item['status']]['data'][index] = item['num']
            
            index += 1

        # print(issues_count.query)
        # print(issues_count)
        # print(status_dict)

        data = {
            # 'categories': ['Arsenal', 'Chelsea', 'Liverpool', 'Manchester United'],
            # 'series': [
            #     {
            #         'name': '新建',
            #         'data': [3, 5, 1, 13]
            #     }, 
            #     {
            #         'name': '处理中',
            #         'data': [14, 8, 8, 12]
            #     }, 
            #     {
            #         'name': '已解决',
            #         'data': [0, 2, 6, 3]
            #     }
            # ]
            'categories': list(user_dict.values()),
            'series': list(status_dict.values())
        }

        return JsonResponse({'status': True, 'data': data})

class ProjectsFileListView(ModelFormMixin, ListView):
    ''' 文件列表 '''

    template_name = 'projects/file_list.html'
    queryset = FileModel.objects.all()
    form_class = FileForm

    def get_queryset(self):
        self.folder_id = self.request.GET.get('folder_id')
        if self.folder_id:
            return self.queryset.filter(project=self.request.project, parent_id=self.folder_id).order_by('-file_type')
        else:
            return self.queryset.filter(project=self.request.project, parent=None).order_by('-file_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # print(context)
        context['nav_li_list'] = []

        if self.folder_id:
            context['folder_id'] = self.folder_id
            # 生成一个目录列表
            # 先获取父级对象
            parent = self.queryset.filter(project=self.request.project, id=self.folder_id, file_type=2).first()
            while parent:
                context['nav_li_list'].insert(0, {'id': parent.id, 'name': parent.name})
                parent = parent.parent

        return context
    
    def get(self, request, *args, **kwargs):
        self.object = None
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        fid = request.POST.get('fid', '')
        if fid.isdecimal():
            self.object = self.get_object(fid)
        
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form):
        parent_object = None
        folder_id = self.request.GET.get('folder_id', '')
        if folder_id.isdecimal():
            parent_object = self.queryset.filter(project=self.request.project, id=folder_id, file_type=2).first()
        form.instance.parent = parent_object
        form.instance.file_type = 2
        form.instance.user = self.request.user
        form.instance.project = self.request.project
        form.save()
        return JsonResponse({'status': True})
    
    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'status': False, 'message': errors})
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        parent_object = None
        folder_id = self.request.GET.get('folder_id', '')

        if folder_id.isdecimal():
            parent_object = self.queryset.filter(project=self.request.project, id=folder_id, file_type=2).first()

        if hasattr(self, "object"):
            kwargs.update({"instance": self.object})

        kwargs.update(
            {
                "request": self.request,
                "parent_object": parent_object,
            }
        )
        return kwargs
    
    def get_object(self, fid):
        obj = self.queryset.filter(project=self.request.project, id=fid, file_type=2).first()
        return obj

class FileDeleteView(View):
    ''' 文件删除 '''

    def get(self, request, *args, **kwargs):

        fid = request.GET.get('fid', '')

        if fid.isdecimal():
            obj = FileModel.objects.filter(project=self.request.project, id=fid).first()
        else:
            return JsonResponse({'status': True})
        
        if obj:

            if obj.file_type == 1:
                # 返还使用空间
                self.request.project.space = F('space') - obj.size
                self.request.project.save()
                # 在硬盘上删除文件
                obj.file_path.delete()
            else:
                # 循环获取该目录下面的所有文件对象（包括子目录）
                total_size = 0
                key_list = []

                delete_obj = [obj,]

                for folder in delete_obj:
                    child_queryset = FileModel.objects.filter(project=request.project, parent=folder).order_by('-file_type')
                    for child in child_queryset:
                        if child.file_type == 2:
                            delete_obj.append(child)
                        else:
                            total_size += child.size
                            key_list.append(child)

                if key_list:
                    for key in key_list:
                        # 在硬盘上删除文件
                        key.file_path.delete()

                if total_size:
                    # 返还使用空间
                    self.request.project.space = F('space') - total_size
                    self.request.project.save()

            # 在数据中删除所有子目录文件和文件夹
            obj.delete()

        return JsonResponse({'status': True})

class FileUploadView(CreateView):
    ''' 文件上传 '''

    template_name = 'projects/file_list.html'
    form_class = FileUploadForm

    def form_valid(self, form):
        file = self.request.FILES.get('file_path')
        folder_id = self.request.GET.get('folder_id')

        # 如果上传文件存在
        if file:
            # 比较该项目使用的空间大小
            # 如果空间小于当前策略
            max_size = self.request.strategy.space * 1024**3
            size = self.request.project.space + file.size
            # print(max_size)
            # print(size)
            if size < max_size:
                # 将文件大小累加到该项目的使用空间大小中
                self.request.project.space = size
                self.request.project.save()
                # 然后在将文件和信息保存到存储空间和数据库中
                form.instance.name = file.name
                form.instance.file_type = 1
                form.instance.size = file.size
                form.instance.user = self.request.user
                form.instance.project = self.request.project

                if folder_id:
                    form.instance.parent_id = folder_id
                    form.save()
                    return JsonResponse({'status': True})
                else:
                    form.save()
                    return JsonResponse({'status': True})
            else:
                # form.add_error('file_path', '文件大小已超过该项目可以使用的空间大小')
                return JsonResponse({'status': False, 'message':'文件大小已超过该项目可以使用的空间大小'})
        
        return JsonResponse({'status': True})
 
class ProjectsWikiView(ListView):
    ''' WIKI列表 '''

    template_name = 'projects/wiki_list.html'
    queryset = Wiki.objects.all()

    def get(self, request, *args, **kwargs):

        '''
        判断一下是否需要用json返回
        '''

        respone = request.GET.get('respone')
        # print(respone)

        if respone:

            wiki_data = self.queryset.filter(project=self.request.project).values('id', 'title', 'parent_id').order_by('depth', 'id')
            # print(list(wiki_data))
            # print(type(wiki_data))
            return JsonResponse({'status': True, 'data': list(wiki_data)})
        
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(project=self.request.project)
    
class WikiDetailView(DetailView):
    ''' WIKI详情 '''

    template_name = 'projects/wiki_detail.html'
    queryset = Wiki.objects.all()
    pk_url_kwarg = 'wikipk'
    context_object_name = 'wiki_object'

class WikiUpdateView(UpdateView):
    ''' WIKI更新  '''

    template_name = 'projects/wiki_update.html'
    queryset = Wiki.objects.all()
    pk_url_kwarg = 'wikipk'
    context_object_name = 'wiki_object'
    form_class = ProjectsWikiForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs
    
    def get_success_url(self):
        url = reverse("projects:wiki", kwargs={'pk': self.kwargs.get('pk'), 'wikipk': self.kwargs.get('wikipk')})
        return url
    
class WikiDeleteView(DeleteView):
    ''' WIKI删除 '''

    queryset = Wiki.objects.all()
    pk_url_kwarg = 'wikipk'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return JsonResponse({'status': True, 'data': ''})
        
class ProjectsWikiCreateView(CreateView):
    ''' WIKI创建 '''

    form_class = ProjectsWikiForm
    template_name = 'projects/wiki_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def form_valid(self, form: BaseModelForm):
        form.instance.project = self.request.project
        if form.instance.parent:
            form.instance.depth = form.instance.parent.depth + 1
        form.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        url = reverse("projects:wiki_list", kwargs={'pk': self.kwargs.get('pk')})
        return url
    
    def get_context_data(self, **kwargs: Any):
        context =  super().get_context_data(**kwargs)
        context['object'] = self.request.project
        return context
    
class ProjectsSettingView(TemplateResponseMixin, View):
    ''' 项目配置 '''

    template_name = 'projects/setting.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response({})
    
class SettingProjectDeleteView(ModelFormMixin, TemplateResponseMixin, View):
    ''' 项目删除 '''

    template_name = 'projects/setting_delete.html'
    form_class = ProjectDeleteForm

    def get(self, request, *args, **kwargs):
        self.object = None
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            # 如果项目标题验证通过
            return self.form_valid(form)
        else:
            # 如果项目标题验证不通过
            # 返回错误信息
            return self.form_invalid(form)
        
    def form_valid(self, form):
        # 获取这个项目所有的文件删除
        file_list = FileModel.objects.filter(project=self.request.project, file_type=1)
        for file in file_list:
            file.file_path.delete()
        self.request.project.delete()
        return redirect(reverse('projects:list'))
        
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
    
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    
class PriceView(LoginRequiredMixin, ListView):
    ''' 价格展示 '''

    template_name = 'projects/price.html'
    queryset = Strategy.objects.filter(s_type=2)

class PayMentView(LoginRequiredMixin, TemplateView):
    ''' 订单展示 '''

    template_name = 'projects/payment.html'

    def get(self, request, *args, **kwargs):

        # 1.获取提交的价格策略
        strategy_obj = Strategy.objects.filter(pk=kwargs.get('pk'), s_type=2).first()
        if not strategy_obj:
            return redirect(reverse('projects:price'))
        
        # 2.要购买数量
        number = request.GET.get('number', '')
        if not number or not number.isdecimal():
            return redirect(reverse('projects:price'))
        number = int(number)
        if number < 1:
            return redirect(reverse('projects:price'))
        
        # 3.计算原价
        origin_price = number * strategy_obj.price

        # 4.如果是已经购买过套餐
        balance = 0
        goods_object = None
        if request.strategy.s_type == 2:
            goods_object = Goods.objects.filter(by_user=request.user, status=1).latest('create_date')
            total_timedelta = goods_object.end_date - goods_object.start_date
            balance_timedelta = goods_object.end_date - datetime.datetime.now()
            if total_timedelta.days == balance_timedelta.days:
                balance = goods_object.amount / total_timedelta.days * (balance_timedelta.days - 1)
            else:
                balance = goods_object.amount / total_timedelta.days * balance_timedelta.days

        if balance >= origin_price:
            return redirect(reverse('projects:price'))
        
        balance = round(balance, 2)

        total_price = origin_price - balance

        kwargs = {
            'strategy_id': strategy_obj.id,
            'number': number,
            'origin_price': str(origin_price),
            'balance': str(balance),
            'total_price': str(total_price),
        }

        conn = get_redis_connection()
        key = f'payment_{request.user.email}'
        conn.set(key, json.dumps(kwargs), 60 * 30)

        kwargs['goods_object'] = goods_object
        kwargs['strategy_object'] = strategy_obj

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class PayView(LoginRequiredMixin, CreateRandom, TemplateView):
    ''' 生成支付宝链接并且跳转到支付链接 '''

    template_name = 'projects/pay.html'

    def get(self, request, *args, **kwargs):

        conn = get_redis_connection()
        key = f'payment_{request.user.email}'
        context_string = conn.get(key)
        if not context_string:
            return redirect(reverse('projects:price'))
        
        context = json.loads(context_string)

        oid = self.uid(request.user.email)

        # 1.生成交易记录，状态为未支付
        Goods.objects.create(
            space=oid,
            status=0,
            by_user=request.user,
            strategy_id=context['strategy_id'],
            amount=context['total_price'],
            num=context['number'],
        )

        # 2.生成支付宝链接
        kwargs['oid'] = oid
        kwargs['callback'] = reverse('projects:pay_callback')
        kwargs.update(context)

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

class PayCallBackView(LoginRequiredMixin, View):
    ''' 支付之后回调 '''

    def post(self, request, *args, **kwargs):

        oid = request.POST.get('oid')
        if not oid:
            pass

        goods_obj = Goods.objects.filter(space=oid).first()
        if not goods_obj:
            pass
        
        start_date = datetime.datetime.now()
        end_year = start_date.year + goods_obj.num
        end_date = start_date.replace(year=end_year)

        goods_obj.status = 1
        goods_obj.start_date = start_date
        goods_obj.end_date = end_date
        goods_obj.save()

        return redirect(reverse('projects:list'))

    
def project_star(request, ty, id):
    ''' 项目标星 '''

    if request.user.is_authenticated:

        if ty == 'my':
            Projects.objects.filter(by_user=request.user, id=id).update(is_markers=True)
            return redirect(reverse('projects:list'))
        
        if ty == 'join':
            Membership.objects.filter(person=request.user, project_id=id).update(is_markers=True)
            return redirect(reverse('projects:list'))
        
        return HttpResponse('错误的请求类型')
    
    return redirect(reverse('user:login_smscod'))

def project_unstar(request, ty, id):
    ''' 项目取消标星 '''

    if request.user.is_authenticated:

        if ty == 'my':
            Projects.objects.filter(by_user=request.user, id=id).update(is_markers=False)
            return redirect(reverse('projects:list'))
        
        if ty == 'join':
            Membership.objects.filter(person=request.user, project_id=id).update(is_markers=False)
            return redirect(reverse('projects:list'))
        
        return HttpResponse('错误的请求类型')
    
    return redirect(reverse('user:login_smscod'))