import json
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth.decorators import login_required
from admin_app.models import *
from user_auth.models import *
from . models import *
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
import re
from django.db.models import *
from django.http.response import JsonResponse
from datetime import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password, check_password
import uuid
import razorpay
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from datetime import datetime
import json




# Create your views here.


# //////////////////////////////////..Dashboard..//////////////////////////
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def Dashboard(request):

    prod = Product.objects.all()
   
    context = {

        'prod': prod
    }
    return render(request,'user_dashboard/dashboard.html',context)


# ///////////////////////////////..All product..//////////////

def All_product(request):

    search = request.GET.get('search')
    sub = request.GET.get('sub')
    sort = request.GET.get('sorting', "")
    filter = request.GET.get('filter', "")
    page = request.GET.get('page', "")

    if not (sub and sort and filter):
        value = Product.objects.all()

    else:
        value = Product.objects.all()

    if search:
        value = Product.objects.filter(name__icontains=search)

    if filter and filter != "all":

        value = value.filter(sub_category=int(filter))

    elif filter and filter == "all":
        value = Product.objects.all()

    if sort:
        value = value.order_by(sort)

    sub = Sub_category.objects.all()

    # paginator = Paginator(value, 2)
    # pro = paginator.get_page(page)

    context = {
        'pro': value,
        'sub': sub
    }

    return render(request, 'user_dashboard/all_product.html', context)

# ////////////////////////////////// end all products ///////////////////////

# //////////////////////////////// search suggestions //////////////////////


@require_GET
@never_cache
def Suggestions(request):

    try:
        prefix = request.GET.get('prefix', '')
        suggestions = []

        #  filter products based on name containing the prefix
        products = Product.objects.filter(name__icontains=prefix)

        # get the names of filtered products

        for product in products:
            suggestions.append(product.name)
        return JsonResponse({'suggestions': suggestions})

    except Exception as e:

        return render(request, 'user_dashboard/error.html')


# ///////////////////////////////// end search suggestions ///////////


# /////////////////////////////////..view product../////////////
@never_cache
def View_product(request, id):

    try:

        pro = get_object_or_404(Product, id=id)
        out_of_stock = Product_size.objects.filter(stock__gte=1, product=id)

        if not out_of_stock:
            stock = False
        else:
            stock = True
        relate = Product.objects.exclude(id=id)[:4]
        product_images = Product_image.objects.filter(product=pro)

        context = {

            'pro': pro,
            'relate': relate,
            'stock': stock,
            'product_images': product_images,

        }

        return render(request, 'user_dashboard/view_product.html', context)

    except Exception as e:
        return render(request, "user_dashboard/error.html")

    # ...................................user profile........................


@login_required(login_url='user_auth/login/')
@never_cache
def User_Profile(request):
    try:

        if request.user.is_authenticated:

            user_details = Custom_User.objects.get(email=request.user)

            context = {
                'user': user_details,
            }

            return render(request, 'user_dashboard/profile.html')

        return redirect("login")

    except TypeError:
        return render(request, 'user_dashboard/error.html')

# .......................EDIT  PROFILE...........
@login_required(login_url='user_auth/login/')
@never_cache
def Edit_profile(request, id):

    try:
        if request.method == 'POST':

            username = request.POST.get("editFirstName")
            email = request.POST.get("editEmail")
            phone = request.POST.get("editphone")
            print("ahaghfagha")

            pattern = r'^[a-zA-Z0-9].*'
            pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            pattern_Phone = r'^(?!0{10}$)\d{10}$'

            if not (username or email or phone):
                messages.error(request, "please fill required field")
                return render(request, "user_dashboard/profile.html")

            if not re.match(pattern, username):
                messages.error(request, "please enter valid user name")
                return render(request, "user_dashboard/profile.html")

            elif not re.match(pattern_email, email):
                messages.error(request, "please enter valid email address")
                return render(request, "user_dashboard/profile.html")

            elif not re.match(pattern_Phone, phone):
                messages.errror(request, "please eneter valid phone number")
                return render(request, 'user_dashboard/profile.html')

            Custom_User.objects.filter(id=id).update(
                username=username, email=email, ph_no=phone)

            return render(request, "user_dashboard/profile.html")

    except TypeError:
        return render(request, "user_dashboard/error.html")

    # .................................... end Edit_profile.......................................

# ............................Address .............

@login_required(login_url='/user_auth/login/')
@never_cache
def Address(request):
    try:
        if request.user.is_authenticated:
            user = Custom_User.objects.get(email=request.user)
            value = User_Address.objects.filter(customuser=user.id)

            context = {

                'value': value
            }

            return render(request, 'user_dashboard/address.html', context)
        return redirect('user_profile')
    except TypeError:
        return render(request, "user_dashboard/error.html")


# ............................add address.................................

@login_required(login_url='user_auth/login/')
@never_cache
def Add_address(request):
    try:
        if request.user.is_authenticated:
            user = Custom_User.objects.get(email=request.user)

            if request.method == "POST":

                name = request.POST.get("name")
                email = request.POST.get("email")
                phone = request.POST.get("phone")
                house = request.POST.get("house")
                street = request.POST.get("street")
                city = request.POST.get("city")
                state = request.POST.get("state")
                country = request.POST.get("country")
                pin_code = request.POST.get("pin_code")
                location = request.POST.get("location")

                pattern = r'^[a-zA-Z0-9].*'
                pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                pattern_Phone = r'^(?!0{10}$)\d{10}$'

                if not (name or email or phone or house or street or city or country or pin_code or location):
                    messages.error(request, "please Fill Required Field")
                    return redirect("address")

                if not all(re.match(pattern, value) and value.strip() for value in [name, email, phone, house, street, city, country, state, pin_code, location,]):
                    messages.error(request, "Please Enter Valid values")
                    return redirect("address")

                elif not re.match(pattern_email, email):
                    messages.error(request, "Please enter valid email address")
                    return redirect("address")

                elif not re.match(pattern_Phone, phone):
                    messages.error(request, "Please enter valid Phone number")
                    return redirect("address")

                value = Custom_User.objects.get(id=user.id)

                User_Address.objects.create(


                    name=name,
                    email=email,
                    phone=phone,
                    house=house,
                    street=street,
                    city=city,
                    state=state,
                    country=country,
                    pin_code=pin_code,
                    location=location,
                    customuser=value,
                )

                return redirect("address")

            return redirect("address")
        return redirect("login")

    except TypeError:
        return render(request, 'dashbord/error.html')


# ...................................delete adddress......................
@login_required(login_url='user_auth/login/')
@never_cache
def Delete_address(request, id):

    try:

        if id:

            User_Address.objects.filter(id=id).delete()

            return redirect("address")

        return redirect("address")

    except TypeError:
        return render(request, 'dashbord/error.html')


# ............................edit address..................
@login_required(login_url='user_auth/login/')
@never_cache
def Edit_address(request):

    try:
        if request.method == "POST":
            E_name = request.POST.get("editname")
            E_name = request.POST.get("editName")
            E_email = request.POST.get("editEmail")
            E_phone = request.POST.get("editphone")
            E_house = request.POST.get("editHouse")
            E_street = request.POST.get("editStreet")
            E_city = request.POST.get("editcity")
            E_state = request.POST.get("editstate")
            E_country = request.POST.get("editcountry")
            E_pin_code = request.POST.get("editpin_code")
            E_location = request.POST.get("editlocation")
            address_id = request.POST.get('editid')

            pattern = r'^[a-zA-Z0-9].*'
            pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            pattern_Phone = r'^(?!0{10}$)\d{10}$'

            if not (E_name or E_email or E_phone or E_house or E_street or E_city or E_country or E_pin_code or E_location):
                messages.error(request, "please Fill Required Field")
                return redirect("address")

            if not all(re.match(pattern, value) and value.strip() for value in [E_name, E_house, E_street, E_city, E_country, E_pin_code, E_location]):
                messages.error(request, "Please Enter Valid values")
                return redirect("address")

            elif not re.match(pattern_email, E_email):
                messages.error(request, "Please enter valid email address")
                return redirect("address")

            elif not re.match(pattern_Phone, E_phone):
                messages.error(request, "Please enter valid Phone number")
                return redirect("address")

            User_Address.objects.filter(id=address_id).update(name=E_name,
                                                              email=E_email,
                                                              phone=E_phone,
                                                              house=E_house,
                                                              street=E_street,
                                                              city=E_city,
                                                              state=E_state,
                                                              country=E_country,
                                                              pin_code=E_pin_code,
                                                              location=E_location
                                                              )
            return redirect("address")
    except TypeError:
        return render(request, "user_dashboard/error.html")

# .......................user cart........................................



@never_cache
def User_cart(request):
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(customuser=request.user)

            sub = request.session.get("sub_total")

            print(cart)
            print(sub)

            if not sub:
                sub_total = 0
                for i in cart:

                    sub_total += int(i.total_price)
                request.session["sub_total"] = sub_total
                sub = request.session.get("sub_total")

            else:

                sub_total = 0
                for i in cart:

                    sub_total += int(i.total_price)
                request.session["sub_total"] = sub_total
                sub = request.session.get("sub_total")

            print(cart)
            print(sub)
            print(sub_total)

            context = {

                'cart': cart,
                'sub_total': sub,
            }
            return render(request, 'user_dashboard/cart.html', context)
        return redirect('login')
    except TypeError:
        return render(request, 'user_dashboard/error.html')


# .................................... ADD TO CART...............................


# @login_required(login_url='/user_auth/login/')
def Add_to_cart(request):
    if request.user.is_authenticated:
        try:
            if request.method == 'POST':
                if request.user.is_authenticated:
                    data = json.loads(request.body)
                    pro_id = data.get('product_id')
                    pro_size = data.get('product_size')
                    pro_qty = data.get('product_qty')
                    product = Product.objects.get(id=pro_id)

                    if (pro_size):
                        if (product):
                            if Cart.objects.filter(customuser=request.user, product=pro_id, size=pro_size).exists():
                                return JsonResponse({'status': "product already in cart"})
                            else:
                                pro_qty = data.get("product_qty")

                                total = int(product.price) * int(pro_qty)

                                val = Cart.objects.create(customuser=request.user,
                                                        product=product,
                                                        size=pro_size,
                                                        qty=pro_qty,
                                                        price=int(product.price),
                                                        total_price=total)

                                if Wishlist.objects.filter(product=pro_id, customuser=request.user).exists():

                                    Wishlist.objects.get(
                                        product=pro_id, customuser=request.user).delete()

                                return JsonResponse({'status': "Product added successfully"})
                        else:
                            return JsonResponse({'status': "No such product found"})
                    else:

                        return JsonResponse({'status': "Please select Your Size"})

                else:

                    messages.error(request, "Login to Continue")

                return redirect("view_product")

        except Exception as e:
            return render(request, 'user_dashboard/error.html')
    else:
        # return redirect('login')
        return JsonResponse({'status': "Please login "})
       
        

# ......................................end add to cart..................................


# //////////////////////////////////   delete from cart ///////////////////////
@login_required(login_url='user_auth/login/')
@never_cache
def Delete_cart(request, id):

    try:
        print(id)
        value = Cart.objects.get(id=int(id))

        if "sub_total" in request.session:

            sub = request.session.get("sub_total")

            sub_total = int(sub) - int(value.total_price)

            if "sub_total" in request.session:
                del request.session["sub_total"]

            request.session["sub_total"] = sub_total
            value.delete()

        return redirect('user_cart')

    except TypeError:
        return render(request, 'user_dashbord/error.html')


# ////////////////////////////////// stock management ,total price ////////////////////////////

@never_cache
@require_POST
@login_required(login_url='/user_auth/login/')
def update_quantity_view(request):
    try:
        if request.method == 'POST':
            cart_item_id = request.POST.get("cartItemId")
            new_quantity = int(request.POST.get('newQuantity'))
            print(new_quantity)
            print(cart_item_id)

            if "sub_total" in request.session:

                del request.session["sub_total"]

            cart_item = get_object_or_404(Cart, id=cart_item_id)

            stock = Product_size.objects.get(
                size=cart_item.size, product=cart_item.product)

            if stock is not None and new_quantity > stock.stock and stock.stock == 0:
                return JsonResponse({'error': f'Not enough  stock available.Current stock:{stock.stock}'}, status=400)
            total = int(cart_item.price) * int(new_quantity)

            if stock.stock >= new_quantity:

                request.session['qty'] = {new_quantity: cart_item_id}
                cart_item.qty = new_quantity
                cart_item.total_price = total
                cart_item.save()

                total_item = Cart.objects.filter(customuser=request.user)
                sub_total = 0

                for i in total_item:
                    sub_total += int(i.total_price)

                cart_subtotal = request.session["sub_total"] = sub_total
                current_stock = stock.stock
                return JsonResponse({'success': True, 'total_price': total, 'cart_subtotal2w': cart_subtotal, 'current_stock': current_stock})

            else:

                total_item = Cart.objects.filter(customuser=request.user)
                sub_total = 0

            for i in total_item:
                sub_total += int(i.total_price)

            cart_subtotal = request.session["sub_total"] = sub_total
            return JsonResponse({'error': f'Not enough stock available. Current stock: {stock.stock}'}, status=400)

    except Exception as e:

        return render(request, 'user_dashboard/error.html')


# ...................................checkout..................................

@login_required(login_url='/user_auth/login')
@never_cache
def Checkout(request):

   
        if request.user.is_authenticated:
            value = Cart.objects.filter(customuser=request.user)
            for i in value:

                pro = Product_size.objects.filter(product=i.product, size=i.size)

                for j in pro:

                    if j.stock < i.qty:

                        messages.error(request, f"{i.product.name} stock not enough")
                        return redirect("user_cart")

            user = request.user
            value = Cart.objects.filter(customuser=user)
            total = request.session.get("sub_total")
            address = User_Address.objects.filter(customuser=user)

            sub_total = 0
            for j in value:

                sub_total += j.price * j.qty

            discount=0
            
                

            cou = None
            if request.method == "POST":
                coupon_id=request.POST.get("coupon_id")
                if coupon_id:
                    cou=Coupon.objects.get(id=coupon_id)
                    total-=cou.discount
                    request.session["coupon_id"]=coupon_id

                else:

                    request.session["coupon_id"]=None

            coupon=Coupon.objects.filter(is_delete=True)
            valid=[]
            for i in coupon:

                if User_Coupon.objects.filter(customuser=request.user,coupon=i.id).exists():
                    pass

                elif i.offer_valid_amount <= sub_total:

                    valid.append(i)

            context = {
                'value' :value,
                'total':total,
                'address' : address,
                'discount' : discount,
                'sub_total' : sub_total,
                'coupon' : valid,
                'coupon_amount' : cou,
            }

            return render(request, 'user_dashboard/checkout.html', context)
        return redirect('login')
   


# ..................................../edit checkout address...........


@login_required(login_url='/user_auth/login')
@never_cache
def Checkout_edit_address(request):
    try:

        if request.method == "POST":

            E_name = request.POST.get("editName")
            E_email = request.POST.get("editEmail")

            E_phone = request.POST.get("editphone")
            E_house = request.POST.get("editHouse")

            E_street = request.POST.get("editStreet")
            E_city = request.POST.get("editcity")

            E_state = request.POST.get("editstate")
            E_country = request.POST.get("editcountry")

            E_pincode = request.POST.get("editpin_code")
            E_location = request.POST.get("editlocation")

            address_id = request.POST.get("editid")

            pattern = r'^[a-zA-Z0-9].*'
            pattern_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            pattern_Phone = r'^(?!0{10}$)\d{10}$'

           
            if not (E_name or E_email or E_phone or E_house or E_street or E_city or E_state or E_country or E_pincode or E_location):
                messages.error(request, "Please Fill Required Field")
                return redirect("address")

            if not all(re.match(pattern, value) and value.strip() for value in [E_name, E_house, E_street, E_city, E_country, E_pincode, E_location]):
                messages.error(request, "Please Enter Valid values")
                return redirect("address")

            elif not re.match(pattern_email, E_email):
                messages.error(request, "Please enter valid email address")
                return redirect("address")

            elif not re.match(pattern_Phone, E_phone):
                messages.error(request, "Please enter valid Phone number")
                return redirect("address")

            User_Address.objects.filter(id=address_id).update(name=E_name,
                                                              email=E_email,
                                                              phone=E_phone,
                                                              house=E_house,
                                                              street=E_street,
                                                              city=E_city,
                                                              state=E_state,
                                                              country=E_country,
                                                              pin_code=E_pincode,
                                                              location=E_location
                                                              )
        return redirect("checkout")
    except Exception as e:
        return render(request, "user_dashboard/error.html")


# .................................add checkout address......................


@login_required(login_url='/user_auth/login')
@never_cache
def Checkout_add_address(request):

    try:
        if request.user.is_authenticated:

            user = Custom_User.objects.get(email=request.user)

            if request.method == "POST":

                name = request.POST.get("add_name")
                email = request.POST.get("add_email")
                phone = request.POST.get("add_phone")
                house = request.POST.get("add_house")
                street = request.POST.get("add_street")
                city = request.POST.get("add_city")
                state = request.POST.get("add_state")
                country = request.POST.get("add_country")
                pincode = request.POST.get("add_pin_code")
                location = request.POST.get("add_location")

                if not (name or email or phone or house or street or city or country or pincode or location):

                    messages.error(request, "please Fill Required Field")
                    return redirect("checkout")

                value = Custom_User.objects.get(id=user.id)

                User_Address.objects.create(name=name,
                                            email=email,
                                            phone=phone,
                                            house=house,
                                            street=street,
                                            city=city,
                                            state=state,
                                            country=country,
                                            pin_code=pincode,
                                            location=location,
                                            customuser=value,
                                            )

                return redirect("checkout")
            return redirect("login")
    except Exception as e:

        return redirect(request, 'user_dashboard/error.html')


# ........................new password.........................
@login_required(login_url='/user_auth/login/')
@never_cache
def Change_password(request):

    try:
        if request.user.is_authenticated:

            if request.method == 'POST':
                old_pass = request.POST.get("old_password")
                new_pass = request.POST.get("new_password")
                con_pass = request.POST.get("con_password")

                if not (old_pass or new_pass or con_pass):
                    messages.error(request, "Please Fill Required Field")
                    return render(request, "user_dashboard/new_pass.html")

                elif new_pass != con_pass:

                    messages.error(
                        request, "New Password and Confirm password doesn't match ")
                    return render(request, "user_dashboard/new_pass.html")

                else:
                    try:
                        user = authenticate(
                            request, email=request.user, password=old_pass)

                    except Exception as e:

                        messages.error(request, "Old Password doesn't match")
                        return render(request, "user_dashboard/new_pass.html")

                    try:

                        user = Custom_User.objects.get(email=request.user)
                        hashed_password = make_password(new_pass)
                        user.password = hashed_password
                        user.save()

                        messages.success(request, "New password updated")
                        return redirect("login")
                    except Exception as e:
                        return render(request, "user_dashboard/error.html")

            return render(request, "user_dashboard/new_pass.html")
    except Exception as e:
        return render(request, 'user_dashboard/error.html')


# /////////////////////////////////////// user order////////////////////
import json
login_required(login_url='/user_auth/login/')
@never_cache
def User_order(request):
    discount = 0
    if request.user.is_authenticated:

        if request.method == 'POST':
            user = Custom_User.objects.get(email=request.user)
            user_id = Custom_User.objects.get(id=user.id)

            data = json.loads(request.body)
            
            
            payment_method = data.get("payment_mode")
            address = data.get("address_id")
         

            total = Cart.objects.filter(customuser=user_id).aggregate(total=Sum('total_price'))
            address = User_Address.objects.filter(id=address)
            for j in address:
                user_add = {'name': j.name, 'email': j.email, 'phone': j.phone,
                            'house': j.house, 'street': j.street, 'city': j.city,
                            'state': j.state, 'country': j.country, 'pin_code': j.pin_code,
                            'location': j.location}

            value = Cart.objects.filter(customuser=request.user)
            for i in value:
                pro = Product_size.objects.filter(product=i.product, size=i.size)
                for j in pro:
                    if j.stock < i.qty:
                        messages.error(request, f"{i.product.name} out of stock ")
                        return redirect("user_cart")

            coupon_id = request.session.get("coupon_id")


            if payment_method == 'cashOnDelivery' and address:
                if total['total'] is not None and total['total'] >= 999:

                    valid_amount = 0
                    if coupon_id:
                        coupon = Coupon.objects.filter(id=coupon_id)
                        for coupon in coupon:
                            total['total'] -= coupon.discount
                            valid_amount = coupon.offer_valid_amount
                            discount = coupon.discount
                            User_Coupon.objects.create(customuser=user_id, coupon=coupon)
                    
                    unique_id = uuid.uuid4()
                    order_id = str(unique_id)[:8]

                    Order.objects.create(user=user_id,
                                        user_address=user_add,
                                        total_amount=total['total'],
                                        payment_type=payment_method,
                                        order_id=order_id,
                                        coupon_valid_amount=valid_amount,
                                        coupon_discount=discount)
                    

                    id = Order.objects.get(order_id=order_id)
                    value = Cart.objects.filter(customuser=user_id)
                    request.session['order_id'] = id.id

                    for i in value:
                        Order_items.objects.create(order=id,
                                       product=i.product,
                                       Sub_category=i.product.sub_category,
                                       qty=i.qty,
                                       size=i.size,
                                       price=i.price,
                                       total_price=i.total_price)
                    for i in value:
                        for j in pro:
                            if j.stock >= i.qty:
                                new_stock = j.stock - i.qty
                                Product_size.objects.filter(product=i.product, size=i.size).update(stock=new_stock)
                                Cart.objects.filter(customuser=user_id).delete()
                                request.session['coupon_id'] = None
                                return JsonResponse({"message": "Payment processed successfully"})

                                return redirect('confirmation')
                            

                            else:
                                messages.error(request, f"{i.product.name} out stock please choose any another product")
                                return redirect("user_cart")
                            
                        else:
                            messages.error(request, f"Select any Address ")
                            return redirect("checkout")
                else:
           
                    messages.error(request, "Cash on delivery is only available for orders above ₹999.")
                    print("......inin")
                    return JsonResponse({"error": "Cash on delivery is only available for orders above ₹999"})
             

            
            elif  payment_method == "wallet" and address:
                        
                                
                            id=Custom_User.objects.get(email=request.user)
                            user=Custom_User.objects.get(id=id.id)
                            total=Cart.objects.filter(customuser=user).aggregate(total=Sum('total_price'))
                            
                            total=int(total['total'])
                            
                            
                                     # ...................Wallet Balance cheking....................
                            if int(user.wallet_bal) > total:
                                    
                                    
                                    #........................ coupon cheking...........
                            
                                valid_amount=0
                                discount=0
                                if coupon_id:
                                    
                                    coupon=Coupon.objects.filter(id=coupon_id)
                                    for coupon in coupon:
                                
                                        total-=coupon.discount      
                                        valid_amount=coupon.offer_valid_amount
                                        discount=coupon.discount
                                        
                                        User_Coupon.objects.create(customuser=user,
                                                                    coupon=coupon)
                    #    ...............order_id genarating.............                
                                            
                                unique_id = uuid.uuid4()
                                order_id = str(unique_id)[:8]    
                                
                    # ..................order creating.................
                                            
                                print(user_id) 
                                Order.objects.create(user = user,
                                                    user_address =user_add,
                                                    total_amount = total,
                                                    payment_type = payment_method,
                                                    order_id = order_id ,
                                                    coupon_valid_amount = valid_amount,
                                                    coupon_discount=discount
                                                                        )  
                                id=Order.objects.get(order_id=order_id)
                                value=Cart.objects.filter(customuser=user_id)
                                request.session['order_id']=id.id
                                
                                for i in value:               
                                        
                                    Order_items.objects.create(order=id,
                                                            product=i.product,
                                                            Sub_category=i.product.sub_category,
                                                            qty=i.qty,
                                                            size=i.size,
                                                            price=i.price,
                                                            
                                                            total_price=i.total_price)
                                
                                #................... wallet amount reduct.................
                                
                                user.wallet_bal -= int(total)
                                user.save()
                                Wallet_Transactions.objects.create(customuser = user,
                                                                   amount = total,
                                                                   resons = 'shopping',
                                                                   add_or_pay = 'pay'
                                                                     
                                                                   )
                                
                                #............................ stock update ...............
                                
                                for i in value:
                                                                        
                                    for j in pro:
                                                                    
                                        if j.stock >= i.qty:
                                                                            
                                            new_stock=j.stock-i.qty
                                            Product_size.objects.filter(product=i.product,size=i.size).update(stock=new_stock)
                                                       
                                                    
                                Cart.objects.filter(customuser=user_id).delete()
                                request.session['coupon_id']=None
                                return JsonResponse({"message": "Payment processed successfully"})

                                return redirect('confirmation')                  
                                        
                            
                            else:
                                
                                messages.error(request,f" Your Wallet is insufficient Please choose any another Payment method")
                                return redirect("checkout")
                              

           
        if request.method == "POST":
            
            data = json.loads(request.body)
            
            
            payment_method = data.get("payment_mode")
            address_id = data.get("address_id")
            print(payment_method)
            print(address_id)

        
            if payment_method == "paid by Razorpay":
                print("Payment")
                address = User_Address.objects.filter(id=address_id)
                for j in address:
                    user_add = {'name': j.name, 'email': j.email, 'phone': j.phone,
                                'house': j.house, 'street': j.street, 'city': j.city,
                                'state': j.state, 'country': j.country, 'pin_code': j.pin_code,
                                'location': j.location}

                valid_amount = 0
                if coupon_id:
                    coupon = Coupon.objects.filter(id=coupon_id)
                    for coupon in coupon:
                        total['total'] -= coupon.discount
                        valid_amount = coupon.offer_valid_amount
                        discount = coupon.discount
                        User_Coupon.objects.create(customuser=user_id, coupon=coupon)

                unique_id = uuid.uuid4()
                order_id = str(unique_id)[:8]

                Order.objects.create(user=user_id,
                                     user_address=user_add,
                                     total_amount=total['total'],
                                     payment_type=payment_method,
                                     order_id=order_id,
                                     coupon_valid_amount=valid_amount,
                                     coupon_discount=discount)

                id = Order.objects.get(order_id=order_id)
                value = Cart.objects.filter(customuser=user_id)
                request.session['order_id'] = id.id

                for i in value:
                    print(i.product.sub_category)
                    Order_items.objects.create(order=id,
                                               product=i.product,
                                               Sub_category=i.product.sub_category,
                                               qty=i.qty,
                                               size=i.size,
                                               price=i.price,
                                               total_price=i.total_price)

                value = Cart.objects.filter(customuser=request.user)
                for i in value:
                    pro = Product_size.objects.filter(product=i.product, size=i.size)
                    for j in pro:
                        if j.stock >= i.qty:
                            new_stock = j.stock - i.qty
                            Product_size.objects.filter(product=i.product, size=i.size).update(stock=new_stock)

                            Cart.objects.filter(customuser=user_id).delete()
                            request.session['coupon_id'] = None
                            return JsonResponse({"message": "Payment processed successfully"})
                            return redirect('confirmation')
                        else:
                            messages.error(request, f"{i.product.name} out stock please choose any another product")
                            return redirect("user_cart")
                else:
                    messages.error(request, f"Select any Address ")
                    return redirect("checkout")
   
    
    else:
        return HttpResponse("User not authenticated.")



# ...................................success order.....................................
@never_cache
def Confirmation(request):

    id = str(request.session.get('order_id'))
    order = Order.objects.get(id=id)
    item = Order_items.objects.filter(order=id)
    pairs = order.user_address.strip('{}').split(',')
    
    my_dict = {}
    for pair in pairs:

        # Check if the pair contains a colon
        if ':' in pair:
            key, value = pair.split(':')
            my_dict[key.strip(" '")] = value.strip(" '")

        else:
            # Handle the case where the pair doesn't contain a colon
            # You might want to log this or handle it differently based on your needs
            print(f"Ignoring invalid pair: {pair}")

    context = {
        'order': order,
        'items': item,
        'house': my_dict.get('house', ''),
        'street': my_dict.get('street', ''),
        'city': my_dict.get('city', ''),
        'country': my_dict.get('country', '')
    }

    return render(request, 'user_dashboard/orderconfirmation.html', context)


# ................................ my order........................................

@login_required(login_url='/user_auth/login/')
@never_cache
def My_Order(request):

    # try:
    user = Custom_User.objects.get(email=request.user)
    orders = Order.objects.filter(user_id=user.id)
    print("0rder:",orders)
    
    if orders:
        addresses = []
        for i in orders:

            pairs = i.user_address.strip('{}').split(',')
            my_dict = {}
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

                addresses.append({'address': address})

            value = zip(orders, addresses)
            context = {

                    'value': value

                }

        return render(request, 'user_dashboard/my_order.html', context)

    return render(request, 'user_dashboard/my_order.html')

        # except Exception as e:
        #      return render(request,'user_dashboard/error.html')


# ..................................... order details...................

@login_required(login_url='/user_auth/login/')
@never_cache
def Order_Details(request, id):

    try:
        order = Order.objects.get(id=id)
        item = Order_items.objects.filter(order_id=id)

        context = {
            'order': order,
            'item': item,
        }

        return render(request, 'user_dashboard/order_details.html', context)
    except TypeError:
        return render(request, 'user_dashboard/error.html')


# ..................................order cancellation...............


@login_required(login_url='/user_auth/login/')
@never_cache
def Cancellation(request, id):
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
    return redirect('my_order')



# ..................................wallet ...................
@login_required(login_url='/user_auth/login/')
@never_cache
def My_Wallet(request):
    wallet=Custom_User.objects.get(email=request.user)
    transaction=Wallet_Transactions.objects.filter(customuser=wallet.id)

    context={
        'wallet' : wallet,
        'transaction' : transaction,
    }

    return render(request,'user_dashboard/wallet.html',context)


# ................................. wallet upi .........................
@never_cache
def Wallet_upi(request):
   
    user_id=Custom_User.objects.get(email=request.user)
    user=Custom_User.objects.get(id=user_id.id)
    client = razorpay.Client(auth=("rzp_test_RjHyjPSCEGAWxg", "FcEx5bKgVzpCgM5bgqBUgXey"))

    return JsonResponse({
        'username' :user.username,'email' : user.email,'phone':user.ph_no,
    })

# ................................ wallet recharge .....................
@login_required(login_url='/user_auth/login/')
@never_cache
def wallet_Recharge(request):
    if request.method == "POST":
       
        amount=request.POST.get("amount")
        payment_type=request.POST.get("payment_mode")
        print(amount)
        print(payment_type)

        user=Custom_User.objects.get(email=request.user)
        new_balance = int(user.wallet_bal) + int(amount)
        user.wallet_bal=new_balance
        user.save()


        Wallet_Transactions.objects.create(customuser=request.user,
                                            amount=amount,
                                            resons=payment_type,
                                            add_or_pay = 'add'
                                            )
    return JsonResponse({'success': "Payment Success"})
   



# ....................................... RAZORPAY ..................................

# @never_cache
def Pay_With_Upi(request):

    #   try:

    print(".....................in in")

    user = Custom_User.objects.get(email=request.user)
    print(user.id, "----gmail_id")
    user_id = user.id

    total = Cart.objects.filter(customuser=user_id).aggregate(
        total=Sum('total_price'))

    coupon_id = request.session.get("coupon_id")
    total = total['total']
    if coupon_id:

        coupon = Coupon.objects.get(id=coupon_id)
        total -= coupon.dicount

    # .........stock cheking ...........

    value = Cart.objects.filter(customuser=request.user)
    for i in value:

        pro = Product_size.objects.filter(product=i.product, size=i.size)

        for j in pro:

            if j.stock < i.qty:

                messages.error(
                    request, f"{i.product.name} out stock please choose any another product")
                return redirect("user_cart")

    client = razorpay.Client(
        auth=("rzp_test_RjHyjPSCEGAWxg", "FcEx5bKgVzpCgM5bgqBUgXey"))
    print("coming call")

    return JsonResponse({
        'total_amount': total, 'username': user.username, 'email': user.email, 'phone': user.ph_no,
    })
    #   except Exception as e:

    #       error=type(e).__name__
    #       typee,code=status_codee(error)

    #       context={
    #           'type' :typee,
    #           'code' : code
    #       }
    #       return render(request, 'dashbord/user_404.html',context)

    # .................END RAZORPAY......................


# .........................Add Wishlist...................................

@login_required(login_url='/user_auth/login/')
@never_cache
def Add_Wishlist(request):

    # try:
 
        if request.method == 'POST':
            data = json.loads(request.body)
            pro_id = int(data.get('product_id'))
        
            pro = Product.objects.get(id=pro_id)
            user = get_object_or_404(Custom_User, email=request.user)

            if Wishlist.objects.filter(customuser=user, product=pro).exists():
                print("alredy")
                return JsonResponse({'success': 'already'})

            if Cart.objects.filter(customuser=user, product=pro).exists():
                print("cart alredy")
                return JsonResponse({'success': 'cart already'})
            Wishlist.objects.create(customuser=user, product=pro)  
            print("add cart")
            return JsonResponse({'success': "added"})
        else:
            print("fails")
            return JsonResponse({'success': False})
    # except Exception as e:

    #     return render(request, 'user_dashboard/error.html')

# ..................................end Add Wishlist..................


# ...............................User wishlist.................


@login_required(login_url='/user_auth/login/')
@never_cache
def User_Wishlist(request):
    #   try:
    print("........121212")
    wish = Wishlist.objects.filter(customuser=request.user)

    context = {
        'wish': wish
    }

    return render(request, 'user_dashboard/wishlist.html',context)
    #   except Exception as e:

    #        return render(request,'user_dashboard/error.html')

# ...............................remove wishlist...............


@login_required(login_url='/user_auth/login/')
@never_cache
def Remove_Wishlist(request, id):
    try:
        Wishlist.objects.get(id=id).delete()
        return redirect("user_wishlist")
    except Exception as e:

        return render(request, 'user_dashboard/error.html')
    

# ................. generating invoice..........................

from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors     
from reportlab.lib.pagesizes import letter
@never_cache 
def download_invoice(request,id):
            
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="sales_invoice.pdf"'

            # Set up PDF canvas
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)

            # Get order items and order details
            order_items = Order_items.objects.filter(order=id)
            order = Order.objects.get(id=id)

            # Set up basic information on the PDF
            p.drawString(250, 750, "Sales Invoice")

            # Display order information
            y_coordinate = 700
            p.drawString(100, y_coordinate, f"Date: {order.created_date.strftime('%Y-%m-%d')}")
            y_coordinate -= 20
            p.drawString(100, y_coordinate, f"Order ID: {order.order_id}")
            y_coordinate -= 20
            p.drawString(100, y_coordinate, f"Customer: {order.user.username}")

            # Extract and display address information
            address = order.user_address.strip('{}').split(',')
            address_dict = {}

            for pair in address:
                print(pair)
                if ':' in pair:

                    key, value = pair.split(':')
                    address_dict[key.strip(" '")] = value.strip(" '")
                else:
                    print(f"Warning: Invalid pair format in order {order.id}: {pair}")

            y_coordinate -= 20
            p.drawString(100, y_coordinate, "Address:")
            for key, value in address_dict.items():
                if key in ['house', 'street', 'city', 'country', 'pin_code']:
                    y_coordinate -= 15
                    p.drawString(120, y_coordinate, value)

            # Create a table and set its style
            data = [['Item', 'Size', 'Quantity', 'Unit Price' ,'Total']]
            for item in order_items:
                data.append([item.product.name, item.size, item.qty, item.price, item.total_price])

            table = Table(data, colWidths=[100, 80, 80, 80, 80,])
            style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(style)

            # Calculate the height of the table
            table_height = len(data) * 15

            # Draw the table on the PDF
            y_coordinate -= max(table_height, 200)  # Ensure enough space for table even if address is large
            table.wrapOn(p, 0, 0)
            table.drawOn(p, 100, y_coordinate)

            # Display "Total Amount" below the table
            total_amount = sum(item.total_price for item in order_items)
            y_coordinate -= (table_height + 20)
            if order.coupon_discount:
                
                    total_amount-=order.coupon_discount
                    p.drawString(380, y_coordinate + 20, f"Coupon: - {order.coupon_discount}")
            
            p.drawString(360, y_coordinate, f"Total Amount: {total_amount}")

            # Close the PDF object cleanly
            p.showPage()
            p.save()

            # Get the value of the BytesIO buffer and write it to the response
            pdf = buffer.getvalue()
            buffer.close()
            response.write(pdf)
            return response
# ...................... STATUS CODE CHECKING ..................

never_cache
def status_codee(error):
    
    if error == 'ValidationError':
        type='Page not Found'
        code=404
        return type,code
    
    elif error =='TypeError':
        type='Bad Request'
        code=400
        return type,code
    
    else:
        type='Page not Found'
        code=400
        return type,code
    

# ....................order return ........................
    
@login_required(login_url='/user_auth/login/')
@never_cache
def Return(request,id):
    order=Order.objects.get(id=id)
    date=timezone.now()
    if order:
         print(",,,,,,,,,,,,,,,,,,,2")
         user_order=Order_items.objects.filter(order_id=id)
         for i in user_order:
             
              stock=Product_size.objects.get(product=i.product,size=i.size)

              stock.stock +=i.qty
              stock.save()


            #   ..........................Order Amount Add to Wallet.....................
              user=Custom_User.objects.get(email=order.user)
              user.wallet_bal=int(user.wallet_bal)+ int(order.total_amount)
              user.save()
              user_id=user.id

              Wallet_Transactions.objects.create(customuser=user,
                                                 amount=order.total_amount,
                                                 resons="order Return",
                                                 created_date=date,
                                                 add_or_pay='add',
                                                 )
              order.status='refunded'
              order.status_date=date
              order.save()
    return redirect("my_order")