from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .models import *
from .models import Order
from user_auth.models import *
from user_dashboard.models import *
from django.db.models import *
import re
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
import datetime
from .views import *
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators  import user_passes_test
from django.views.decorators.cache import never_cache,cache_control
from django.contrib.auth.decorators import login_required
from io import BytesIO
from reportlab.pdfgen import canvas
from django.db.models.functions import Coalesce
from datetime import datetime
from django.utils import timezone
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors     
from django.db.models.functions import Coalesce
from reportlab.lib.pagesizes import letter
from django.db.models import Sum, Value


# Create your views here.

            # ........... User Priventing Authentication................#
def admin_required(view_func):
    actual_decorator =user_passes_test(
        lambda a:a.is_authenticated and a.is_staff,
        login_url='admin_login'
    )
    return actual_decorator(view_func)

               # ...........End  User Priventing Authentication................
    
              #.......................Admin Authentication.................. 
@never_cache
def Admin(request):
    try:


    
        if 'email_admin' in request.session:
            return redirect("admin_dashboard")
        
        if request.method == "POST":
            email = request.POST.get("email")
            password = request.POST.get("password")
            print(email,password)
            users = authenticate(request,username=email, password=password)

            if users is not None and users.is_staff:
                login(request, users)
                request.session['email_admin'] = email
                return redirect("admin_dashboard")
            else:
                messages.error(request, "Email or Password mismatch")
                return render(request, "admin/admin_login.html")
            
        return render(request, "admin/admin_login.html")
    
    except Exception as e:

        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)


#.....................End admin Authentication.............................

# ........................Admin Dashboard................................
@admin_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/admin_app/")
@never_cache
def Admin_dashboard(request):
    try:
        if request.method =="POST":
                
                start_date=request.POST.get("startDate")
                end_date=request.POST.get("endDate")
                if start_date and end_date:
                    total_sale=Order.objects.filter(status__in=['pending','processing','shipped','delivered'], created_date__range=(start_date, end_date)).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
                    all_amount=Order.objects.filter(created_date__range=(start_date, end_date)).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
                    total_sale=total_sale['total']//1000
                    all_amount=all_amount['total']//1000
                    cod_total=Order.objects.filter(payment_type="cashOnDelivery", created_date__range=(start_date, end_date),status__in=['pending','processing','shipped','delivered']).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
                    upi_total=Order.objects.filter(payment_type="paid by Razorpay",created_date__range=(start_date, end_date),status__in=['pending','processing','shipped','delivered']).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
                    wallet_total=Order.objects.filter(payment_type="wallet",created_date__range=(start_date, end_date),status__in=['pending','processing','shipped','delivered']).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
                    pending=Order.objects.filter(status='pending',created_date__range=(start_date, end_date)).aggregate(total=Count("status"))
                    processing=Order.objects.filter(status='processing',created_date__range=(start_date, end_date)).aggregate(total=Count("status"))
                    shipped=Order.objects.filter(status='shipped',created_date__range=(start_date, end_date)).aggregate(total=Count("status"))
                    delivered=Order.objects.filter(status='delivered',created_date__range=(start_date, end_date)).aggregate(total=Count("status"))
                    cancelled=Order.objects.filter(status='cancelled',created_date__range=(start_date, end_date)).aggregate(total=Count("status"))
                    refund=Order.objects.filter(status='refunded',created_date__range=(start_date, end_date)).aggregate(total=Count("status"))
                    all=Order.objects.filter(created_date__range=(start_date, end_date)).aggregate(total=Count('id'))
                    
                    context={
                            'total_sale' : total_sale,
                            'all_amount' : all_amount,
                            'cod_total'  : cod_total['total'],
                            'upi_total'  : upi_total['total'],
                            'wallet_total':wallet_total['total'],
                            'pending'    : pending['total'],
                            'procrssing' : processing['total'],
                            'sipped'     : shipped['total'],
                            'delivered'  : delivered['total'],
                            'cancelled'  : cancelled['total'],
                            'refund'     : refund['total'],
                            'all_category': all['total'],
                            }
                    return render(request,"admin/admin_dashbaord.html",context)
                    

                return render(request,"admin/admin_dashboard.html")
        
        else:
            total_sale=Order.objects.exclude(Q(status="cancelled") &~ Q(status="refunded")).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
            all_amount=Order.objects.aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
            total_sale=total_sale['total']//1000
            all_amount=all_amount['total']//1000
            cod_total=Order.objects.filter(payment_type="cashOnDelivery").aggregate(total=Sum('total_amount'))
            upi_total=Order.objects.filter(payment_type="paid by Razorpay").aggregate(total=Sum('total_amount'))
            wallet_total=Order.objects.filter(payment_type="wallet",).aggregate(total=Sum('total_amount'))
            wallet=Order.objects.filter(payment_type="wallet")
            pending=Order.objects.filter(status='pending').aggregate(total=Count("status"))
            processing=Order.objects.filter(status='processing').aggregate(total=Count("status"))
            shipped=Order.objects.filter(status='shipped').aggregate(total=Count("status"))
            delivered=Order.objects.filter(status='delivered').aggregate(total=Count("status"))
            cancelled=Order.objects.filter(status='cancelled').aggregate(total=Count("status"))
            refund=Order.objects.filter(status='refunded').aggregate(total=Count("status"))
            all=Order.objects.all().aggregate(total=Count('id'))
            best_selling_products = Order_items.objects.filter(order__status__in=['delivered', 'completed']).values('product__name').annotate(total_sales=Sum('qty')).order_by('-total_sales')[:10]
            best_selling_categories = Order_items.objects.filter(order__status__in=['delivered', 'completed']).values('product__sub_category__category__name').annotate(total_sales=Sum('qty')).order_by('-total_sales')[:10]

          


                    


            context={
                        'total_sale' : total_sale,
                        'all_amount' : all_amount,
                        'cod_total'  : cod_total['total'],
                        'upi_total'  : upi_total['total'],
                        'wallet_total':wallet_total['total'],
                        'pending'    : pending['total'],
                        'procrssing' : processing['total'],
                        'sipped'     : shipped['total'],
                        'delivered'  : delivered['total'],
                        'cancelled'  : cancelled['total'],
                        'refund'     : refund['total'],
                        'all_category': all['total'],
                        'best_selling_products': best_selling_products,
                        'best_selling_categories':best_selling_categories,
                        
                    }
            return render(request,"admin/admin_dashboard.html",context)
    
    except Exception as e:
        print("----",e)
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

        
#......................Admin logout...................

def Admin_logout(request):
    try:


        if 'email_admin' in request.session:
            
            email_admin_value =request.session.get('email_admin')
            del request.session['email_admin']
            logout(request)
            
            return redirect("admin_login")
    except Exception as e:

        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

#........................End Admin ......................
    

#....................User List............................
    
@admin_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url="/admin_app/")
@never_cache
def User_list(request):
    try:

    
        user=Custom_User.objects.filter(is_staff=False).values()

        context={
            "user":user
        }

        return render(request,"admin/user_list.html",context)
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

#.....................end user list.......................


#......................user unblock..........................
@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def User_unblock(request,id):
    try:

    
        user=Custom_User.objects.get(id=id)
        user.is_active=True
        user.save()
        return redirect("user_list")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

#..................... end user unblock................

#.......................user block.......................
@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def User_block(request,id):
    try:
    
        user=Custom_User.objects.get(id=id)
        user.is_active=False
        user.save()
        return redirect("user_list")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

#....................end user block...........


#....................product category...............

@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url="admin_app")
@never_cache

def Category_list(request):
    try:
    
        ca =Category.objects.all()
        context ={
            'ca' : ca
        }

        return render(request,"admin/category.html",context)
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)


# ..............................Add Category....................

@admin_required
@login_required(login_url="/admin_app/")
@never_cache

def Add_category(request):
    try:

        if request.method == 'POST':
            name = request.POST.get("category_name")

            if Category.objects.filter(name=name).exists():

                messages.error(request,"This Item Already Exist")
                return redirect("category_list")
            
            Category.objects.create(name=name)
            return redirect("category_list")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

    

# ...............................change status.............
    
@admin_required
@login_required(login_url="/admin_app/")
@never_cache

def Change_status(request,id):
    try:


        ca=Category.objects.get(id=id)

        if not ca.is_deleted:
            ca.is_deleted =True
            ca.save()
        
        else:
            ca.is_deleted =False
            ca.save()
        
        return redirect('category_list')
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)


# .......................... delete category..................
@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def Delete_category(request,id):
    try:


        ca = Category.objects.get(id=id)
        ca . delete()
        return redirect("category_list")
    except Exception as e:

        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

# /////////////////////////////update category//////////////////////////////
    
@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def Update_category(request,id):
    try:
        if request.method == 'POST':
            name=request.POST.get("category_name")



            if Category.objects.filter(name=name).exist():
                
                messages.error(request,"This Category Already Exist")
                return redirect("category_list")
            
            Category.objects.filter(id=id).update(name=name)
        return redirect("category_list")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)
    
         
#.............................. sub category............................

@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url="admin_app")
@never_cache

def sub_category(request):
    try:

        sub = Sub_category.objects.all()
        main = Category.objects.all()
        today= datetime.today().date()
        

        context={
            'sub':sub,
            'main':main,
            
        }
        return render(request,"admin/sub_category.html",context)
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

# ..................... Add Sub category.......................
@admin_required
@login_required(login_url="admin_app")
@never_cache

def Add_sub_category(request):
    try:

        if request.method =='POST':
            sub=request.POST.get("category_name")
            ca=request.POST.get("category_type")

            if Sub_category.objects.filter(name=sub,category=ca).exists():

                messages.error(request,"Sub Category Already Exist")
                return redirect("sub_category")
            
            id=Category.objects.get(id=ca)
            Sub_category.objects.create(name=sub,category=id)

            return redirect("sub_category")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)
    

# ...........................change status ...........................
@admin_required
@login_required(login_url="admin_app")
@never_cache

def Status_change(request,id):
    try:


        status=Sub_category.objects.get(id=id)

        if not status.is_deleted:

            status.is_deleted=True
            status.save()
        else:
            status.is_deleted= False
            status.save()

        return redirect("sub_category")
    except Exception as e: 

        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

# ........................ update sub category..............
@admin_required
@login_required(login_url="admin_app")
@never_cache

def Update_sub_category(request,id):
    try:
    
        if request.method == 'POST':
            name=request.POST.get("category_name")

            if Sub_category.objects.filter(name=name).exists():
                messages.error(request,"Sun Category Already Exist")
                return redirect("sub_category")
            
            Sub_category.objects.filter(id=id).update(name=name)

            return redirect("sub_category")
    except Exception as e: 
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)
        
# ///////////////////////// delete sub category ////////////////
@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def Delete_sub_category(request,id):
    try:

        sub=Sub_category.objects.get(id=id)
        sub.delete()
        
        return redirect("sub_category")
    except Exception as e: 
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

#.....................................  product   .......................................

@admin_required
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@login_required(login_url="admin_app")
@never_cache
def Product_list(request):
    try:
        pro=Product.objects.all()
        sub=Sub_category.objects.filter(is_deleted=True)
        img=Product_image.objects.all().prefetch_related("product_set")
        print(pro,sub)


        context={
            'pro' : pro,
            'sub' : sub,
            'img': img
            

        }

        return render(request,"admin/product.html",context)
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

# ///////////////////////// product status /////////////////
@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def Product_status(request,id):
    try:
   
        status=Product.objects.get(id=id)
        print(status)
        value=Product_size.objects.all()
        
        for i in value:
            print(i.product)
            if status == i.product:
            
                    if not status.is_deleted:
                        
                        status.is_deleted = True
                        status.save()
                        return redirect("product_list")
                    else:
                        
                        status.is_deleted = False
                        status.save()
                        return redirect("product_list")
        else:
            messages.error(request, "Please add any size")
            return redirect("product_list")
    except Exception as e: 
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)
    
# /////////////////// add product //////////////////
from django.core.files.base import ContentFile
@admin_required
@login_required(login_url="/admin_app/")
@never_cache                     
def Add_product(request):
    try:

    
        if request.method == "POST" :
            
            name=request.POST.get("product_name")
            price=int(request.POST.get("price"))
            discount=int(request.POST.get("discount"))
            sub_category=request.POST.get("category_type")
            description=request.POST.get("description")
            m_image=request.FILES.get("m_image")
            r_images=request.FILES.getlist("r_images")
            if int(price) < 1:
                
                messages.error(request, "Invalid Price . Price Should Be Above Zero ")
                return redirect("product_list")
            
            if int(discount) < 0:
                
                messages.error(request, "Invalid Discound . Discound Should Be Zero or  Above Zero ")
                return redirect("product_list")
            
                
            sub=Sub_category.objects.get(id=sub_category)
            pro_id=Product.objects.create(name=name,
                                        price=price,
                                        discount=discount,
                                        sub_category=sub,
                                        description=description,
                                        image=m_image)
            
            for i in range(len(r_images)):

                Product_image.objects.create(product=pro_id,image_url=r_images[i])
            
                
            return redirect("product_list")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)
    
# /////////////////////  delete product ///////////////////
@admin_required
@login_required(login_url="/admin_app/")
@never_cache     
def Delete_product(request,id):
    try:

   
        pro=Product.objects.get(id=id)
        pro.delete()
        
        return redirect("product_list")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)
                    
# ////////////////////////  update product //////////////////////
@admin_required
@login_required(login_url="/admin_app/")
@never_cache     
def Update_product(request,id):
    try:

    
        if request.method == "POST" :
            
            up= Product.objects.get(id=id)
            
            name=request.POST.get("product_name")
            price=request.POST.get("price")
            discount=float(request.POST.get("discount"))
            sub_category=request.POST.get("category_type")
            description=request.POST.get("description")
            image=request.FILES.get("image")
            r_image=request.FILES.getlist("related_images")
            delete=request.POST.getlist("selected_images")
            
            
        
            if int(price) < 1:
                
                messages.error(request, "Invalid Price . Price Should Be Above Zero ")
                return redirect("product_list")
            
            if discount < 0:
                
                messages.error(request, "Invalid Discound . Discound Should Be Zero or Above Zero ")
                return redirect("product_list")
            
                
            sub=Sub_category.objects.get(id=sub_category)
            
            up.name=name
            up.price=price
            up.discount=discount
            up.description=description
            up.sub_category=sub


            if image:
                up.image=image
                
            up.save()

            if delete and r_image:
                for i in delete:
                    Product_image.objects.filter(id=int(i)).delete()
                
                for j in r_image:
                    Product_image.objects.create(product=up,image_url=j)

            elif delete:
                for i in delete:
                    Product_image.objects.filter(id=int(i)).delete()

            elif r_image:
                for i in r_image:
                    Product_image.objects.create(product=up,image_url=i)
            
            
        return redirect("product_list")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

# ////////////////////// add size //////////////////
@admin_required
@login_required(login_url="/admin_app/")
@never_cache     
def Add_size(request,id):
    try:

        
        if request.method == "POST":
            
            size=request.POST.get("size")
            stock=request.POST.get("stock")
            
            print(type (id))
            if int(size) <= 0 or int(stock) <= 0 :
                    
                    messages.error(request, "Invalid Size or Stock .Size and Stock Should Be Above Zero ")
                    return redirect("product_list")
                
            else:
                value=Product.objects.get(id=id)
                if Product_size.objects.filter(size=size,product=value).exists():
                    
                    messages.error(request, "This size already listed")
                    return redirect("product_list")
                
                else:
                        value=Product.objects.get(id=id)
                        
                        Product_size.objects.create(size=size,stock=stock,product=value)
            
        return redirect("product_list")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)


# /////////////////////////////////////edit size ///////////////////////
@admin_required
@login_required(login_url="/admin_app/")
@never_cache     
def Edit_size(request,id):
    try:
    
        if request.method == 'POST':
            
            for size_obj in Product_size.objects.filter(product_id=id):
                
                size = request.POST.get('size' + str(size_obj.id))
                stock = request.POST.get('stock' + str(size_obj.id))
                
                if int(size) < 0 or int(stock) < 0 :
                    
                    messages.error(request, "Invalid Size or Stock .Size and Stock Should Be Above Zero ")
                    return redirect("product_list")
                
                else:
                    size_obj.stock=stock 
                    size_obj.size=size 
                    size_obj.save()

            
        return redirect("product_list")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)


#.............................. user orders .....................

@admin_required
@login_required(login_url="/admin_app/")
@never_cache     
def User_Orders(request):
    try:

        orders = Order.objects.all()
        addresses = []

        for order in orders:
            pairs = order.user_address.strip('{}').split(',')
            my_dict = {}

            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':')
                    my_dict[key.strip(" '")] = value.strip(" '")
                else:
                    print(f"Warning: Invalid pair format in order {order.id}: {pair}")

            address = {
                'house': my_dict.get('house', ''),
                'street': my_dict.get('street', ''),
                'city': my_dict.get('city', ''),
                'country': my_dict.get('country', ''),
                'pin_code': my_dict.get('pin_code', ''),
                'location': my_dict.get('location', ''),
                'phone': my_dict.get('phone', ''),
                'name': my_dict.get('name', ''),
            }
            
            addresses.append(address)

        value = zip(orders, addresses)
        

        context = {
            'value': value,
        }

        return render(request, "admin/user_orders.html", context)
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)



# ///////////////////////////  user order list ///////////////////////////
        
@admin_required
@login_required(login_url="/admin_app/")
@never_cache     
def Order_List(request,id):
    try:


        order=Order.objects.get(id=id)
        item=Order_items.objects.filter(order_id=id)

        context={
            'order':order,
            'item': item,
        }

        return render(request,'admin/order_list.html',context)
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)


# /////////////////////////   order status //////////////////
@admin_required
@login_required(login_url="/admin_app/")
@never_cache     
def Order_Status(request,id):
    try:


        if request.method =='POST':

            action=request.POST.get("action")

        order=Order.objects.get(id=id)
        date=timezone.now()
        if action and action != 'refunded':

            order.status=action
            order.status_date=date
            order.save()

        return redirect('user_orders')
    except Exception as e: 
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)


# .................... cancal order............
@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def cancel_order(request,id):
    try:
        order = Order.objects.get(id=id)
        date = timezone.now()
        if order:

            if order.payment_type == "cashOnDelivery":
                user_order = Order_items.objects.filter(order_id=id)
                for i in user_order:

                    stock = Product_size.objects.get(product=i.product, size=i.size)
                    stock.stock += i.qty
                    stock.save()
                
                if order.status == "delivered":
                    user=Custom_User.objects.get(id=order.user)
                    user.wallet_bal=int(user.wallet_bal)+ int(order.total_amount)
                    user.save()
                    Wallet_Transactions.objects.create(customuser = user,
                                                    amount=order.total_amount,
                                                    resons= 'order Cancellation',
                                                    add_or_pay ='add',
                    )
                order.status= 'cancelled'
                order.status_date=date
                order.save()

            elif order.payment_type == 'paid by Razorpay':
                user_order = Order_items.objects.filter(order_id=id)
                for i in user_order:

                    stock = Product_size.objects.get(product=i.product, size=i.size)

                    stock.stock += i.qty
                    stock.save()
                    

        # .........................order Amount Add To Wallet .................
                    user=Custom_User.objects.get(id=order.user)
                    user.wallet_bal = int(user.wallet_bal) + int(order.total_amount)
                    user.save()
                    Wallet_Transactions.objects.create(customuser = user,
                                                        amount= order.total_amount,
                                                        resons= 'order Cancellation',
                                                        add_or_pay = 'add',               
                                                        )
                    order.status= 'refunded'
                    order.status_date=date
                    order.save()
            
            elif order.payment_type == "wallet" :
                user_order=Order_items.objects.filter(order_id=id)
                for i in user_order:

                    stock=Product_size.objects.get(product=i.product,size=i.size)

                    stock.stock += i.qty
                    stock.save()


                    # .....................................Order Amount Add to Wallet .....................

                    user=Custom_User.objects.get(id=order.user)
                    user.wallet_bal += int(order.total_amount)
                    user.save()
                    Wallet_Transactions.objects.create(customuser = user,
                                                        amount= order.total_amount,
                                                        resons= 'order Cancellation',
                                                        add_or_pay = 'add',               
                                                        )
                    order.status= 'refunded'
                    order.status_date=date
                    order.save()
        return redirect('user_orders')
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)



# ......................coupon view .................
@admin_required
@login_required(login_url="/admin_app/")
@never_cache 
def Coupon_View(request):
    try:


        coupon=Coupon.objects.all()
        context={
            'coupon':coupon
        }
        return render(request,'admin/coupon.html',context)
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)


#............................ Add Coupon .....................
@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def Add_Coupon(request):
    try:


        if request.method == "POST":
            name = request.POST.get("name")
            valid_amount = int(request.POST.get("valid_amount"))
            dis =int(request.POST.get("discount"))

            pattern = r'^[a-zA-Z0-9].*'

            if not re.match(pattern,name or valid_amount or dis):

                messages.error(request,"Please Enter Valid inputs")
                return redirect('coupon_view')
            
            elif valid_amount < 100 :

                messages.error(request,"Invalid offer valid amount . Valid Offer Amount  Should Be 100 or more Than 100")
                return redirect('coupon_view')
            
            elif dis < 0 or (valid_amount/2) < dis:

                messages.error(request,"Invalid Discound . Discound Should Be Zero or  less than Offer Valid Amount 50%")
                return redirect('coupon_view')
            
            else:

                Coupon.objects.create(name=name,
                                        offer_valid_amount=valid_amount,
                                        discount=dis
                                        )
                
        return redirect("coupon_view")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)

# ....................... delete coupon .....................

def Delete_Coupon(request,id):
    try:
        Coupon.objects.get(id=id).delete()
        return redirect("coupon_view")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)



# ....................... Coupon status ................
@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def Coupon_Status(request,id):
    try:


        coupon=Coupon.objects.get(id=id)

        if coupon.is_delete:

            coupon.is_delete=False
            coupon.save()

        else:
            coupon.is_delete=True
            coupon.save()


        return redirect("coupon_view")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)



# ....................delete coupon ..................

@admin_required
@login_required(login_url="/admin_app/")
@never_cache
def Delete_Coupon(request,id):
    try:


        Coupon.objects.get(id=id).delete()
        return redirect("coupon_view")
    except Exception as e:
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)


# ...............SALES REPORT ......................

@never_cache
def Sales_Report(request):
    try:

        if request.method == "POST":

            start_date =request.POST.get("startDate")
            end_date = request.POST.get("endDate")
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="sales_Reports.pdf"'
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)


            # sales report heading

            p.setFont("Helvetica-Bold", 16)
            p.drawString(220, 750, "Sales Report")

            # start and end date
            p.setFont("Helvetica", 12)
            p.drawString(50, 720, f"Sale Started: {start_date}")
            p.drawString(50, 700, f"Sale Ended: {end_date}")


            # transaction heading

            p.setFont("Helvetica-Bold", 16)
            p.drawString(220, 670, "Transactions")


            # transaction table

            total_sale = Order.objects.filter(status__in=['pending', 'processing', 'shipped', 'delivered'], created_date__range=(start_date, end_date)).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
            all_amount = Order.objects.filter(created_date__range=(start_date, end_date)).aggregate(total=Sum("total_amount"))
            cod_total = Order.objects.filter(payment_type="cashOnDelivery", created_date__range=(start_date, end_date), status__in=['pending', 'processing', 'shipped', 'delivered']).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
            upi_total = Order.objects.filter(payment_type="paid by Razorpay", created_date__range=(start_date, end_date), status__in=['pending', 'processing', 'shipped', 'delivered']).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))
            wallet_total = Order.objects.filter(payment_type="wallet", created_date__range=(start_date, end_date), status__in=['pending', 'processing', 'shipped', 'delivered']).aggregate(total=Coalesce(Sum('total_amount'), Value(0)))

            data_transactions = [['Cash on Delivery', 'Online payment', 'Wallet', 'Total Revenue', 'Total Sale']]
            data_transactions.append([cod_total['total'], upi_total['total'], wallet_total['total'], total_sale['total'], all_amount['total']])
            table_transactions = Table(data_transactions, colWidths=[100, 80, 80, 80, 80])

            # Set style for the transaction table

            style = TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
            table_transactions.setStyle(style)
            # Calculate the top 5 best-selling products
            top_selling_products = Order_items.objects.filter(
                order__created_date__range=(start_date, end_date)
            ).values('product__name').annotate(
            total_quantity=Sum('qty')
    )       .order_by('-total_quantity')[:5]
            
            

            # Top 5 Best-Selling Products Heading
            p.setFont("Helvetica-Bold", 16)
            p.drawString(220, 320, "Top 5 Best-Selling Products")

            # Top 5 Best-Selling Products table
            data_top_selling = [['Product', 'Total Quantity Sold']]
            for product in top_selling_products:
                data_top_selling.append([product['product__name'], product['total_quantity']])
            table_top_selling = Table(data_top_selling, colWidths=[150, 150])

            # Set style for the top selling products table
            table_top_selling.setStyle(style)

            # Draw the top selling products table on the PDF
            table_top_selling.wrapOn(p, 0, 0)
            table_top_selling.drawOn(p, 120, 180)


            # Draw the transactions table on the PDF

            table_transactions.wrapOn(p, 0, 0)
            table_transactions.drawOn(p, 50, 600)

            # Product Summary Heading
            
            p.setFont("Helvetica-Bold", 16)
            p.drawString(220, 520, "Product Summary")

            # Product Summary table
            data_product_summary = [['Product', 'Quantity', 'Price', 'Total Amount']]
            products = Product.objects.all()
            for product in products:
                product_summary = Order_items.objects.filter(order__created_date__range=(start_date, end_date), product=product.id).aggregate(total=Sum('qty'), total_price=Sum('total_price'))
                data_product_summary.append([product.name, product_summary['total'], product.price, product_summary['total_price']])
                table_product_summary = Table(data_product_summary, colWidths=[80, 80, 80, 100])

                # Set style for the product summary table
                table_product_summary.setStyle(style)

                # Draw the product summary table on the PDF
                table_product_summary.wrapOn(p, 0, 0)

                # Define the starting Y coordinate for drawing the table
                start_y_coordinate = 500

                # Calculate the height of the table
                table_height = table_product_summary._height

                # Calculate the ending Y coordinate for drawing the table
                end_y_coordinate = start_y_coordinate - table_height

                # Draw the table at the calculated Y coordinate
                table_product_summary.drawOn(p, 120, end_y_coordinate)

                p.showPage()
                p.save()

                # Get the value of the BytesIO buffer and write it to the response
                pdf = buffer.getvalue()
                buffer.close()
                response.write(pdf)
                return response
            return redirect('admin_dashboard')
    except Exception as e: 
        error=type(e).__name__
        typee,code=status_code(error)
            
        context={
            'type' :typee,
            'code' : code
        }
        return render(request, 'admin/admin_404.html',context)
    
    

# .....................STATUS CODE CHECKING....................
    
never_cache
def status_code(error):

    if error == 'ValidationError':
        type='Page not Found'
        code=404
        return type,code
    
    elif error == 'TypeError':
        type='Bad Request'
        code=400
        return type,code
    else:
        type='Page not Found'
        code=404
        return type,code











        