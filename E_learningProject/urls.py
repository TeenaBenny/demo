"""
URL configuration for E_learningProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from instructorApp import views as instructorView
from studentApp import views as studentView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('instructor/register',instructorView.InstructorView.as_view(),name='instructor_reg'),
    path('home',studentView.StudentView.as_view(),name='student_home'),
    path('course/detail/<int:id>',studentView.CourseDetail.as_view(),name='course_detail'),
    path('student/register',studentView.StudentRegisterView.as_view(),name="student_register"),
    path('/',studentView.StudentLogin.as_view(),name="student_login"),
    path('add/cart/<int:id>',studentView.AddToCart.as_view(),name="add_to_cart"),
    path('cart/list',studentView.CartSummaryView.as_view(),name="cart_list"),
    path('cart/delete/<int:id>',studentView.CartDelete.as_view(),name="cart_delete"),
    path('checkout',studentView.CheckOutView.as_view(),name="checkout_view"),
    path('confirm',studentView.PaymentConfirm.as_view(),name="confirm"),
    path('mycourse',studentView.MyCourse.as_view(),name="mycourse"),
    path('lesson/<int:id>',studentView.LessonView.as_view(),name="lesson_view"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
