from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse

from projects.models import Projects, Membership



class GetProjectMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):

        
        request.project = None

        if not request.path_info.startswith('/projects/manage/'):
            return
        
        if request.user.is_authenticated:
            pk = view_kwargs.get('pk')
            # print(pk)

            my_project = Projects.objects.filter(by_user=request.user, pk=pk).first()

            if my_project:
                request.project = my_project
                return
            
            join_project = Membership.objects.filter(person=request.user, project=pk).first()
            # print(join_project)

            if join_project:
                request.project = join_project.project
                return
            
            return redirect(reverse('projects:list'))
    
        return redirect(reverse('user:login_smscod'))