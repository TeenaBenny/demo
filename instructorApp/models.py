from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from embed_video.fields import EmbedVideoField
from django.db.models import Max

# Create your models here.

class User(AbstractUser):
    role=models.CharField(max_length=100,default="student")

    def __str__(self):
        return self.username

class InstructorProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='instructor')
    profile_pic=models.ImageField(upload_to='profile_pic',null=True,blank=True,default='profile_pic/default.png')
    expertise=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.user.username
    
def create_profile(sender,instance,created,**kwargs):
    if created and instance.role=='instructor':
        InstructorProfile.objects.create(user=instance)

post_save.connect(create_profile,User)


class Category(models.Model):
    category_name=models.CharField(max_length=100,unique=True)

    def __str__(self):
        return self.category_name

class Course(models.Model):
    owner=models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    category=models.ManyToManyField(Category,related_name="category")
    title=models.CharField(max_length=200)
    description=models.TextField()
    image=models.ImageField(upload_to="course_image",null=True,blank=True)
    thumbnail=EmbedVideoField()
    price=models.DecimalField(decimal_places=2,max_digits=6)
    added_date=models.DateField(auto_now_add=True)
    updated_date=models.DateField(auto_now=True)

    def __str__(self):
        return self.title

class Module(models.Model):
    course_instance=models.ForeignKey(Course,on_delete=models.CASCADE,related_name="module")
    title=models.CharField(max_length=100,unique=True)
    order=models.IntegerField()

    def __str__(self):
        return f"{self.course_instance.title}+{self.title}"

    def save(self,*args,**kwargs):
        max_order=Module.objects.filter(course_instance=self.course_instance).aggregate(max=Max("order")).get("max")or 0
        self.order=max_order+1
        super().save(*args,**kwargs)

class Lesson(models.Model):
    module_instance=models.ForeignKey(Module,on_delete=models.CASCADE,related_name="lesson")
    title=models.CharField(max_length=100,unique=True)
    video=EmbedVideoField()
    order=models.IntegerField()


    def __str__(self):
        return f"{self.module_instance}={self.title}"
    
    def save(self,*args,**kwargs):
        max_order=Lesson.objects.filter(module_instance=self.module_instance).aggregate(max=Max("order")).get("max")or 0
        self.order=max_order+1
        super().save(*args,**kwargs)
    
class Cart(models.Model):
    user_instance=models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_cart')
    course_instance=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='course_cart')

    def __str__(self):
        return f"{self.user_instance.username}+{self.course_instance.title}"
    
class Order(models.Model):
    course_instance=models.ManyToManyField(Course,related_name="order")
    user_instance=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_order")
    total=models.DecimalField(max_digits=10,decimal_places=2)
    rap_order_id=models.CharField(max_length=100,null=True,blank=True)
    ordered_date=models.DateField(auto_now_add=True)
    is_paid=models.BooleanField(default=False)

    def __str__(self):
        return self.user_instance.username