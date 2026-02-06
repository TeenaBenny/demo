from django.shortcuts import render
from django.views import View
from instructorApp.models import User
from instructorApp.form import InstructorCreateForm
from django.http import HttpResponse

# Create your views here.
class InstructorView(View):
    def get(self,request):
        form=InstructorCreateForm()
        return render(request,'instructor_reg.html',{'form':form})
    
    def post(self,request):
        form_instances=InstructorCreateForm(request.POST)
        print(form_instances)
        if form_instances.is_valid():
            form_instances.instance.is_superuser=True
            form_instances.instance.is_staff=True
            form_instances.instance.role='instructor'
            form_instances.save()
            return HttpResponse('user added')

