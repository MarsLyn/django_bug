from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from .views import (
    ProjectsListView, 
    ProjectsCreateView,
    ProjectsDashboardView,
    DashboardIssuesChartView,
    ProjectsIssuesListView,
    IssuesDeatilView,
    IssuesUpdateView,
    IssuesReplyView,
    InviteCodeCreateView,
    InviteJoinView,
    ProjectsStatisticsView,
    StatisticsPriorityView,
    StatisticsUserView,
    ProjectsFileListView,
    FileDeleteView,
    FileUploadView,
    ProjectsWikiView,
    WikiDetailView,
    ProjectsWikiCreateView,
    WikiUpdateView,
    WikiDeleteView,
    ProjectsSettingView,
    SettingProjectDeleteView,
    PriceView,
    PayMentView,
    PayView,
    PayCallBackView,
    project_star,
    project_unstar,
)

urlpatterns = [
    path('', ProjectsListView.as_view(), name='list'),
    path('create/', ProjectsCreateView.as_view(), name='create'),
    path('manage/', include([
        path('<int:pk>/dashboard/', ProjectsDashboardView.as_view(), name='dashboard'),
        path('<int:pk>/dashboard/issues/chart/', DashboardIssuesChartView.as_view(), name='issues_chart'),
        path('<int:pk>/issues/', ProjectsIssuesListView.as_view(), name='issues_list'),
        path('<int:pk>/issues/<int:issues_id>/', IssuesDeatilView.as_view(), name='issues_detail'),
        path('<int:pk>/issues/<int:issues_id>/update/', csrf_exempt(IssuesUpdateView.as_view()), name='issues_update'),
        path('<int:pk>/issues/<int:issues_id>/reply/', IssuesReplyView.as_view(), name='issues_reply'),
        path('<int:pk>/issues/invite/url/', InviteCodeCreateView.as_view(), name='invite_url'),
        path('<int:pk>/statistics/', ProjectsStatisticsView.as_view(), name='statistics'),
        path('<int:pk>/statistics/priority/', StatisticsPriorityView.as_view(), name='priority'),
        path('<int:pk>/statistics/user/', StatisticsUserView.as_view(), name='statistics_user'),
        path('<int:pk>/file/', ProjectsFileListView.as_view(), name='file_list'),
        path('<int:pk>/file/delete/', FileDeleteView.as_view(), name='file_delete'),
        path('<int:pk>/file/upload/', FileUploadView.as_view(), name='file_upload'),
        path('<int:pk>/wiki/', ProjectsWikiView.as_view(), name='wiki_list'),
        path('<int:pk>/wiki/<int:wikipk>/', WikiDetailView.as_view(), name='wiki'),
        path('<int:pk>/wiki/<int:wikipk>/update/', WikiUpdateView.as_view(), name='wiki_update'),
        path('<int:pk>/wiki/<int:wikipk>/delete/', WikiDeleteView.as_view(), name='wiki_delete'),
        path('<int:pk>/wiki/create/', ProjectsWikiCreateView.as_view(), name='create'),
        path('<int:pk>/setting/', ProjectsSettingView.as_view(), name='setting'),
        path('<int:pk>/setting/delete/', SettingProjectDeleteView.as_view(), name='delete'),
    ]), None, None),
    path('issues/invite/join/<str:code>/', InviteJoinView.as_view(), name='invite_join'),
    path('price/', PriceView.as_view(), name='price'),
    path('<int:pk>/payment/', PayMentView.as_view(), name='payment'),
    path('pay/', PayView.as_view(), name='pay'),
    path('pay/callback/', PayCallBackView.as_view(), name='pay_callback'),
    path('star/<str:ty>/<int:id>/', project_star, name='star'),
    path('unstar/<str:ty>/<int:id>/', project_unstar, name='unstar'),
]

app_name = 'projects'