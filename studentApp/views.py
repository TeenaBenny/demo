from django.shortcuts import render,redirect
from django.views import View
from instructorApp.models import Course,Cart,Order,Lesson,Module
from instructorApp.form import InstructorCreateForm
from django.contrib.auth import authenticate,login
from django.utils.decorators import method_decorator
from django.db.models import Sum
import razorpay
# Create your views here.

RZP_KEY_ID="rzp_test_RifDzt4pKQWr1a"
RZP_KEY_SECRET="3Vf1UdmeIw4SyJqGD4MU9d90"


class StudentView(View):
    def get(self,request):
        courses=Course.objects.all()
        ordered_course=Order.objects.filter(user_instance=request.user).values_list('course_instance',flat=True)
        print(ordered_course)
        return render(request, 'index.html',{'courses':courses,'ordered_course':ordered_course})
    
class CourseDetail(View):
    def get(self,request,**kwargs):
        course=Course.objects.get(id=kwargs.get('id'))
        return render(request,'course_detail.html',{'course':course})
    
class StudentRegisterView(View):
    def get(self,request):
        form=InstructorCreateForm()
        return render(request,'student.html',{'form':form})
    
    def post(self,request):
        form_instance=InstructorCreateForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            return redirect("student_login")

    
class StudentLogin(View):
    def get(self,request):
        form=InstructorCreateForm()
        return render(request,'student.html',{'form':form})
    

    def post(self,request):
        uname=request.POST.get("username")
        psw=request.POST.get("password")
        res=authenticate(request,username=uname,password=psw)
        if res:
            login(request,res)
            if res.role=="student":
                return redirect("student_home")
            else:
                return redirect("student_login")

def login_required(fn):
    def wrapper(request,*args,**kwargs):
        if not request.user.is_authenticated:
            return redirect("student_login")
        else:
            return fn(request,*args,**kwargs)
    return wrapper
        
@method_decorator(login_required,name="dispatch")
class AddToCart(View):
    def get(self,request,*args,**kwargs):
        user=request.user
        course=Course.objects.get(id=kwargs.get("id"))
        Cart.objects.get_or_create(user_instance=user,course_instance=course)
        return redirect("student_home")
    
class CartSummaryView(View):
    def get(self,request,*args,**kwargs):
        cart_list=Cart.objects.filter(user_instance=request.user)
        cart_total=sum(cart.course_instance.price for cart in cart_list)
        return render(request,'cart_summary.html',{'cart_list':cart_list,'cart_total':cart_total})
    
class CartDelete(View):
    def get(self,request,*args,**kwargs):
        cart_item=Cart.objects.get(id=kwargs.get('id'))
        cart_item.delete()
        return redirect('cart_list')

class CheckOutView(View):
    def get(self,request,*args,**kwargs):
        cart_list=Cart.objects.filter(user_instance=request.user) 
        user=request.user
        total=cart_list.aggregate(total=Sum("course_instance__price")).get("total") 
        print(total)
        order_instance=Order.objects.create(user_instance=user,total=total)
        if cart_list:
            for cart in cart_list:
                order_instance.course_instance.add(cart.course_instance)
                cart.delete()
                client = razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))

                DATA = {
                    "amount": float(total*100),
                    "currency": "INR",
                    "receipt": "receipt#1",
                    "notes": {
                        "key1": "value3",
                        "key2": "value2"
                    }
                }
                payment=client.order.create(data=DATA)
                print(payment)
                order_id=payment.get('id')
                order_instance.rap_order_id=order_id
                order_instance.save()
                context={
                    "total":float(total*100),
                    "key_id":RZP_KEY_ID,
                    "order_id":order_id
                }
                return render(request,'payment.html',context)
from django.views.decorators.csrf import csrf_exempt
@method_decorator(csrf_exempt,name='dispatch')            
class PaymentConfirm(View):
    def post(self,request,*args,**kwargs):
        client = razorpay.Client(auth=(RZP_KEY_ID,RZP_KEY_SECRET))
        res=client.utility.verify_payment_signature(request.POST)
        print(res)
        order_id=request.POST.get('razorpay_order_id')
        order_instance=Order.objects.get(rap_order_id=order_id)
        order_instance.is_paid=True
        order_instance.save()
        return redirect('student_home')


class MyCourse(View):
    def get(self,request):
        orders= Order.objects.filter(user_instance=request.user,is_paid=True)
        return render(request,'mycourse.html',{'orders':orders})
    
class LessonView(View):
    def get(self, request,*args,**kwargs):
        course=Course.objects.get(id=kwargs.get('id'))
        print(request.GET)
        module_id=request.GET.get('module')if 'module' in request.GET else course.module.all().first().id
        module_instance=Module.objects.get(id=module_id)
        lesson_id=request.GET.get('lesson')if 'lesson' in request.GET else module_instance.lesson.all().first().id
        lesson_instance=Lesson.objects.get(id=lesson_id)
        if 'lesson' in request.GET:
            lesson_id=request.GET.get("lesson")
        else:
            lesson_id==lesson_instance

        return render(request,'lesson.html',{'course':course,'lesson':lesson_instance})









