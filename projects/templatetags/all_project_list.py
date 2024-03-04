from django import template
from django.urls import reverse


from projects.models import Projects, Membership


register = template.Library()


@register.inclusion_tag('projects/all_project_list.html')
def all_project_list(request):

    my = Projects.objects.filter(by_user=request.user)
    join = Membership.objects.filter(person=request.user)

    return {'my': my, 'join': join, 'request': request}
    # return {'my': [], 'join': []}

@register.inclusion_tag('projects/menu_project_list.html')
def menu_project_list(request):

    all_list_tag = [
        {'title': '概览', 'url': reverse('projects:dashboard', kwargs={'pk': request.project.id})},
        {'title': '问题', 'url': reverse('projects:issues_list', kwargs={'pk': request.project.id})},
        {'title': '统计', 'url': reverse('projects:statistics', kwargs={'pk': request.project.id})},
        {'title': 'wiki', 'url': reverse('projects:wiki_list', kwargs={'pk': request.project.id})},
        {'title': '文件', 'url': reverse('projects:file_list', kwargs={'pk': request.project.id})},
        {'title': '配置', 'url': reverse('projects:setting', kwargs={'pk': request.project.id})},
        {'title': '价格', 'url': reverse('projects:price')},
    ]

    for item in all_list_tag:
        if request.path_info.startswith(item['url']):
            item['class'] = 'bg-info'

    return {'all_list_tag': all_list_tag}

@register.inclusion_tag('projects/setting_nav.html')
def setting_nav(request):

    all_list_tag = [
        {'title': '我的资料', 'url': reverse('projects:setting', kwargs={'pk': request.project.id})},
        {'title': '修改密码', 'url': '#'},
        {'title': '删除项目', 'url': reverse('projects:delete', kwargs={'pk': request.project.id})},
    ]

    for item in all_list_tag:
        if request.path_info == item['url']:
            item['class'] = 'active'
            item['aria_current'] = 'true'

    return {'all_list_tag': all_list_tag}

@register.inclusion_tag('projects/paginate.html')
def paginate(request, page_obj, paginator):
    page_num = request.GET.get('page')

    all_list_tag = []

    for page in paginator:
        all_list_tag.append({'num': page.number, 'url': f"?page={page.number}"})

    for item in all_list_tag:
        if not page_num:
            item['class'] = 'active'
            break
        if int(page_num) == item['num']:
            item['class'] = 'active'
        
    new_request = request.GET.copy()
    # print(new_request)
    new_request.pop('page', None)
    # print(new_request)
    return {'all_list_tag': all_list_tag, 'page_obj': page_obj, 'paginator': paginator, 'request': new_request}