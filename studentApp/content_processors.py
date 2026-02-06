from instructorApp.models import Order

def course_count(request):
    if request.user.is_authenticated:
        orders=Order.objects.filter(user_instance=request.user,is_paid=True).count()
        return{'order_count':orders}
    else:
        return{'order_count':0}