from ftplib import error_temp
from itertools import product
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from category.models import Category
from shopping_web.models import Product, MemberOrder, MemberOrderItem
from shopping_web.models import VisitorOrderItem
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from datetime import date
from django.forms.models import model_to_dict
import json


def getNumberOfItemsInCart(request):

    number_of_items_in_cart = 0
    
    if not request.session.exists(request.session.session_key):
        number_of_items_in_cart = 0
        session_key = None
    else:        
        if request.user.username != "":            
            session_key = request.session.session_key
            
            if 'order_id' in request.session:
                order_id = request.session.get('order_id')
                order = MemberOrder.objects.filter(customer_id=request.user.id).filter(transaction_id=None).first()

                # if order.transaction_id is None:
                if order:
                    orderItem = MemberOrderItem.objects.filter(order_id=order_id)
                else:
                    orderItem = []
            else:
                try:
                    order = MemberOrder.objects.filter(customer_id=request.user.id).filter(transaction_id=None).first()
                    print("ORDER : ", order)
                    if order:
                        order_id = order.id                        
                        orderItem = MemberOrder.objects.filter(memberorderitem__order_id=order_id)
                    else:
                        orderItem = []
                except ObjectDoesNotExist:
                    orderItem = []
            
            number_of_items_in_cart = len(orderItem)
        else:
            session_key = request.session.session_key
            print("session_key = ", session_key)            
            cart = VisitorOrderItem.objects.filter(session_id=session_key)
            number_of_items_in_cart = len(cart)

    return number_of_items_in_cart, session_key
        

def index(request):
    # session_key = None

    username = request.user.username
    number_of_items_in_cart = 0

    categories = Category.objects.all()
    products = Product.objects.all().order_by('category_id', 'product_name')
    
    # นับจำนวนสินค้าที่เพิ่มในตะกร้า

    # if not request.session.exists(request.session.session_key):
    #     number_of_items_in_cart = 0
        
    # else:        
    #     if username != "":            
    #         session_key = request.session.session_key
            
    #         if 'order_id' in request.session:
    #             order_id = request.session.get('order_id')
    #             orderItem = MemberOrderItem.objects.filter(order_id=order_id)
    #         else:
    #             try:
    #                 order = MemberOrder.objects.filter(customer_id=request.user.id).first()
    #                 print("ORDER : ", order)
    #                 if order:
    #                     order_id = order.id
    #                     orderItem = MemberOrder.objects.filter(memberorderitem__order_id=order_id)
    #                 else:
    #                     orderItem = []
    #             except ObjectDoesNotExist:
    #                 orderItem = []
            
    #         number_of_items_in_cart = len(orderItem)
    #     else:
    #         session_key = request.session.session_key
    #         print("session_key = ", session_key)            
    #         cart = VisitorOrderItem.objects.filter(session_id=session_key)
    #         number_of_items_in_cart = len(cart)
    
    number_of_items_in_cart, session_key = getNumberOfItemsInCart(request)

    paginator = Paginator(products,8)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1

    try:
        productPerPage = paginator.page(page)
    except (EmptyPage,InvalidPage):
        productPerPage = paginator.page(paginator.num_pages)

    return render(request,'index.html', {
        'categories':categories,
        'products':productPerPage, 
        'session_key': session_key, 
        'number_of_items_in_cart': number_of_items_in_cart
    })

def product_detail(request, **kwargs):

    # product_id = Product.o
    categories = Category.objects.all()

    product_id = kwargs['pid']
    print("product_id=", product_id)

    # TODO
    product = Product.objects.filter(id=product_id).get()

    number_of_items_in_cart, session_key = getNumberOfItemsInCart(request)
    # selct * from shopping_web_product where id=4
    # print("product : ", product.price)

    return render(request,'product_detail.html',{
        'categories':categories, 
        'product':product,
        'session_key': session_key, 
        'number_of_items_in_cart': number_of_items_in_cart
    })

def contact(request):
    categories = Category.objects.all()
    
    # นับจำนวนสินค้าที่เพิ่มในตะกร้า
    # session_key = request.session._get_or_create_session_key()    
    # cart = VisitorOrderItem.objects.filter(session_id=session_key)
    
    
    number_of_items_in_cart, session_key = getNumberOfItemsInCart(request)

    return render(request,'contact.html', {
        'number_of_items_in_cart': number_of_items_in_cart,
        'categories':categories,
        'number_of_items_in_cart': number_of_items_in_cart,
    })

def search(request):  
    categories = Category.objects.all()
    
    number_of_items_in_cart, session_key = getNumberOfItemsInCart(request)

    if request.method == "POST":        
        search = request.POST.get("search")
        print("search: ", search)

        # TODO 
        products = Product.objects.filter(product_name__icontains=search)
        # where product_name like 'Fancy%'

        print("product: ", products)
    else:
        print(request.method)
    
    return render(request,'search.html', 
        {
            'categories':categories, 
            'products':products, 
            'search':search,
            'number_of_items_in_cart': number_of_items_in_cart,
        })


def cart(request):
    carts = []
    username = request.user.username 
    categories = Category.objects.all()

    number_of_items_in_cart = 0
    total = 0
    shipping_cost = 50
    grand_total = 0

    # นับจำนวนสินค้าที่เพิ่มในตะกร้า
    if not request.session.exists(request.session.session_key):
        number_of_items_in_cart = 0
    else:        
        if username != "":            
            session_key = request.session.session_key
            
            if 'order_id' in request.session:
                order_id = request.session.get('order_id')
                print("ABCDE : ", order_id)
                order = MemberOrder.objects.filter(customer_id=request.user.id).filter(transaction_id=None).first()
                if order.transaction_id is not None:
                    carts = []
                else:
                    carts = MemberOrderItem.objects.filter(order_id=order_id)
            else:
                try:
                    order = MemberOrder.objects.filter(customer_id=request.user.id).filter(transaction_id=None).first()

                    if order:                                           
                        
                        if order.transaction_id is not None:
                            carts = []
                        else:
                            carts = MemberOrder.objects.filter(memberorderitem__order_id=order.id)

                    else:
                        carts = []
                except ObjectDoesNotExist:
                    carts = []

        else:
            session_key = request.session.session_key            
            carts = VisitorOrderItem.objects.filter(session_id=session_key)
            number_of_items_in_cart = len(carts)

        for item in carts:
            total = total + (item.product.price * item.quantity)

        if len(carts) > 0:
            grand_total = total + shipping_cost
        else:
            total = 0            
            grand_total = 0
            shipping_cost = 0
            
        number_of_items_in_cart = len(carts)

    return render(request,'cart.html', {
        'number_of_items_in_cart': number_of_items_in_cart,
        'carts': carts,
        'categories':categories,
        'total': '{:0,.2f}'.format(total),
        'shipping_cost': '{:0,.2f}'.format(shipping_cost),
        'grand_total': '{:0,.2f}'.format(grand_total),
    })



def userLogin(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    is_user = False
    error_message = ""


    paginator = Paginator(products,4)
    try:
        page = int(request.GET.get('page','1'))
    except:
        page = 1

    try:
        productPerPage = paginator.page(page)
    except (EmptyPage,InvalidPage):
        productPerPage = paginator.page(paginator.num_pages)


    if request.method == 'POST':
        
        email =  request.POST.get("email")
        password =  request.POST.get("password")
        session_key = request.session._get_or_create_session_key()
        cart = VisitorOrderItem.objects.filter(session_id=session_key)

        # TODO - ตรวจสอบว่าเป็นผู้ใช้ที่ลงทะเบียนไว้แล้วหรือยัง                
        user = authenticate(request, username=email, password=password)
        print("user: ", user)

        if user is not None:        
            login(request, user)

            # หลังจากล็อคอินได้ให้ตรวจสอบว่ามีออเดอร์ที่ยังไม่ได้ทำการสั่งซื้อไว้หรือไม่                        
            if 'order_id' in request.session:
                order_id = request.session.get('order_id')

                order = MemberOrder.objects.filter(id=order_id).filter(transaction_id=None)
                if order.transaction_id is not None:
                    request.session['order_id'] = order_id
                    orderItem = []
                else:
                    orderItem = MemberOrderItem.objects.filter(order_id=order_id)
            else:
                try:
                    order = MemberOrder.objects.filter(customer_id=request.user.id).filter(transaction_id=None).first()
                    print("ORDERrr : ", order)
                    if order:
                        order_id = order.id
                        request.session['order_id'] = order_id
                        orderItem = MemberOrder.objects.filter(memberorderitem__order_id=order_id)
                    else:
                        request.session['order_id'] = None
                        orderItem = []
                except ObjectDoesNotExist:
                    request.session['order_id'] = None
                    orderItem = []
            
            number_of_items_in_cart = len(orderItem)
            print("XXX : ", number_of_items_in_cart)
            is_user = True
        else:
            is_user = False
        
        if is_user:
            # return render(request,'index.html',{'categories':categories})
            return redirect("/")

            '''
            return render(request,'index.html', {
                'categories':categories,
                'products':productPerPage, 
                'session_key': session_key, 
                'number_of_items_in_cart': len(cart)
            })
            '''
        else:
            error_message = "ใส่ข้อมูลผู้ใช้ไม่ถูกต้อง"
            return render(request,'login.html',{'categories':categories, 'email': email, 'error_message': error_message})
    else:
        email = ""
        return render(request,'login.html',{'email': email,'categories':categories})


def register(request): 

    is_error = True
    errorMessage = ""
    
    categories = Category.objects.all()

    if request.method == "POST":                
        firstName = request.POST.get("firstName")
        lastName = request.POST.get("lastName")
        email = request.POST.get("email")
        address = request.POST.get("address")
        password = request.POST.get("password")
        rePassword = request.POST.get("rePassword")

        if firstName == "":
            is_error = True
            errorMessage = "กรุณาป้อนชื่อ"
        else:
            is_error = False
            errorMessage = ""

        # is_error = True if lastName == "" else False
        if not is_error:
            if lastName == "":
                is_error = True
                errorMessage = "กรุณาป้อนนามสกุล"
            else:
                is_error = False
                errorMessage = ""

        # is_error = True if email == "" else False
        if not is_error:
            if email == "":
                is_error = True
                errorMessage = "กรุณาป้อนอีเมล"
            else:
                is_error = False
                errorMessage = ""

        if not is_error:
            if password == rePassword:
                is_error = True if password == "" else False
                is_error = True if rePassword == "" else False

                if len(password) < 6:
                    is_error = True
                    errorMessage = "รหัสผ่านไม่ถูกต้อง"
                else:
                    is_error = False
            else:
                is_error = True
                errorMessage = "รหัสผ่านไม่ถูกต้อง"
    

        # ถ้าไม่มี Error เลยให้ไปที่หน้า Login
        if is_error:
            return render(request,'register.html',{
                'categories':categories,
                'firstName': firstName,
                'lastName': lastName,
                'email': email,
                'address': address,
                'password': password,
                'rePassword': rePassword,
                'errorMessage': errorMessage
                })            
        else:
            # TODO : เก็บค่าลง Database
            if not is_error:
                print("เก็บค่าลงฐานข้อมูล")
                user = User(username=email, is_superuser=False, is_staff=True, is_active=True, password=make_password(password))
                user.save()

            return render(request,'login.html',{'categories':categories})

    else:
        firstName = ""
        lastName = ""
        email = ""
        address = ""
        password = ""
        rePassword = ""
        
        return render(request,'register.html',{
            'categories':categories,
            'firstName': firstName,
            'lastName': lastName,
            'email': email,
            'address': address,
            'password': password,
            'rePassword': rePassword
            })


def shoes(request):
    products = Product.objects.all()    
    categories = Category.objects.all()

    number_of_items_in_cart, session_key = getNumberOfItemsInCart(request)

    return render(request,'shoes.html', 
    {
        'products':products,'categories':categories, 
        'number_of_items_in_cart': number_of_items_in_cart,
    })


def bags(request):   
    products = Product.objects.all() 
    categories = Category.objects.all()
    
    number_of_items_in_cart, session_key = getNumberOfItemsInCart(request)

    return render(request,'bags.html',{'products':products, 'categories':categories, 'number_of_items_in_cart': number_of_items_in_cart})


def payment(request):
    is_error = True
    firstName = ""
    lastName = ""
    address = ""
    province = ""
    district = ""
    subDistrict = ""
    postCode = ""
    telephone = ""
    email = ""
    error_message =""

    carts = []
    categories = Category.objects.all()
    
    number_of_items_in_cart = 0
    number_of_items_in_cart, session_key = getNumberOfItemsInCart(request)
    
    username = request.user.username 
    categories = Category.objects.all()

    number_of_items_in_cart = 0
    total = 0
    shipping_cost = 50
    grand_total = 0

    if request.method == "POST":        
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')
        address = request.POST.get('address')
        province = request.POST.get('province')
        district = request.POST.get('district')
        subDistrict = request.POST.get('subDistrict')
        postCode = request.POST.get('postCode')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email')

    if firstName == "":
        is_error = True
        error_message = "กรุณาป้อนชื่อ"
    elif lastName == "":
        is_error = True
        error_message = "กรุณาป้อนนามสกุล"
    elif address == "":
        is_error = True
        error_message = "กรุณาป้อนที่อยู่"
    elif province == "":
        is_error = True
        error_message = "กรุณาป้อนจังหวัด"        
    elif district == "":
        is_error = True
        error_message = "กรุณาป้อนอำเภอ"
    elif subDistrict == "":
        is_error = True
        error_message = "กรุณาป้อนตำบล"
    elif postCode == "":
        is_error = True
        error_message = "กรุณาป้อนรหัสไปรษณีย์"
    elif telephone == "":
        is_error = True
        error_message = "กรุณาป้อนเบอร์ติดต่อ"
    elif email == "":
        is_error = True
        error_message = "กรุณาป้อนอีเมล"
    else:
        is_error = False
        error_message = ""

    # นับจำนวนสินค้าที่เพิ่มในตะกร้า
    if not request.session.exists(request.session.session_key):
        number_of_items_in_cart = 0        
    else:        
        if username != "":            
            session_key = request.session.session_key
            
            if 'order_id' in request.session:
                order_id = request.session.get('order_id')
                carts = MemberOrderItem.objects.filter(order_id=order_id)
            else:
                try:
                    order = MemberOrder.objects.filter(customer_id=request.user.id).filter(transaction_id=None).first()
                    print("ORDER : ", order)
                    if order:                        
                        carts = MemberOrder.objects.filter(memberorderitem__order_id=order.id)
                    else:
                        carts = []
                except ObjectDoesNotExist:
                    carts = []
        else:
            session_key = request.session.session_key
            carts = VisitorOrderItem.objects.filter(session_id=session_key)
            number_of_items_in_cart = len(carts)

        for item in carts:
            total = total + (item.product.price * item.quantity)

        grand_total = total + shipping_cost
        number_of_items_in_cart = len(carts)


    if is_error:
        return render(request,'payment.html', {
            'number_of_items_in_cart': number_of_items_in_cart,
            'carts': carts,
            'categories':categories,
            'total': '{:0,.2f}'.format(total),
            'shipping_cost': '{:0,.2f}'.format(shipping_cost),
            'grand_total': '{:0,.2f}'.format(grand_total),
            'firstName': firstName,
            'lastName': lastName,
            'address': address,
            'province': province,
            'district': district,
            'subDistrict': subDistrict,
            'postCode': postCode,
            'telephone': telephone,
            'email': email,
            'is_error': is_error,
            'error_message': error_message,
        })
    else:


        if username != "":
            print("TODO 22222")
            
            if 'order_id' in request.session:
                order_id = request.session.get('order_id')
                order = MemberOrder.objects.filter(customer_id=request.user.id).filter(transaction_id=None).first()
                order.transaction_id = 1
                order.save()

                request.session['order_id'] = None
                print("ORDER ID ", order_id)

            else:
                print("TODO 3")
                try:
                    order = MemberOrder.objects.filter(customer_id=request.user.id).filter(id=order_id).filter(transaction_id=None).get()
                    print("ORDER : ", order)
                except ObjectDoesNotExist:
                    print("ERROR!!")

        else:
            print("TODO 44")
            session_key = request.session.session_key            
            carts = VisitorOrderItem.objects.filter(session_id=session_key).all()
            carts.delete()

            request.session.order_id = None
        
        
        # print("!!! : ", request.session.get('order_id'))

        return render(request,'thankyou.html', {
            'number_of_items_in_cart': 0,
            'categories':categories,
            'is_error': is_error,
            'error_message': error_message,
        })        


@csrf_exempt
def refresh_cart(request):
    # กำหนดค่าเริ่มต้น
    username = request.user.username        
    is_error = True
    error_message = ""
    number_of_items_in_cart = 0    
    total = 0
    shipping_cost = 50
    grand_total = 0

    cart_list = []
    record = {}

    # รับค่า Item จากหน้า UI แล้วลบ 
    item_id = request.POST.get('item_id')
    method = request.POST.get('method')
    quantity = request.POST.get('quantity')

    print("%s | %s | %s" % (item_id, method, quantity))
    # return False

    if username != "":
        order_item = MemberOrderItem.objects.get(id=item_id)
        if method == "add":
            order_item.quantity = order_item.quantity + int(quantity)
        elif method == 'substract':
            order_item.quantity = order_item.quantity - int(quantity)
        else:
            print("ERROR")

            
    else:
        order_item = VisitorOrderItem.objects.get(id=item_id)
        if method == "add":
            order_item.quantity = order_item.quantity + int(quantity)
        elif method == "substract":
            order_item.quantity = order_item.quantity - int(quantity)
        else:
            print("ERROR")

    order_item.save()    

    # ส่งข้อมูล item ที่เหลือในตะกร้ากลับไปที่หน้า UI
    if not request.session.exists(request.session.session_key):
        number_of_items_in_cart = 0

        print("TODO 1")
    else:
        if username != "":
            print("TODO 2")
            session_key = request.session.session_key
            
            if 'order_id' in request.session:
                order_id = request.session.get('order_id')
                carts = MemberOrderItem.objects.filter(order_id=order_id).all()
            else:
                print("TODO 3")
                try:
                    order = MemberOrder.objects.filter(customer_id=request.user.id).filter(transaction_id=None).first()
                    print("ORDER : ", order)
                    if order:                        
                        carts = MemberOrder.objects.filter(memberorderitem__order_id=order.id).all()
                    else:
                        carts = []
                except ObjectDoesNotExist:
                    carts = []

            for item in carts:
                total = total + (item.product.price * item.quantity)

            grand_total = total + shipping_cost
            number_of_items_in_cart = len(carts)

        else:
            print("TODO 4")
            session_key = request.session.session_key            
            carts = VisitorOrderItem.objects.filter(session_id=session_key).all()
            number_of_items_in_cart = len(carts)

    
    if carts:
        total = 0
        grand_total = 0

        for item in carts:
            item_id = item.id
            product_name = item.product.product_name
            product_price = item.product.price
            product_image = item.product.image.url
            product_quantity = item.quantity

            total = total + (product_price * product_quantity)
            print("%s | %s * %s = %s" % (item_id, product_price, product_quantity, product_price * product_quantity))

            record = {
                "item_id": item_id,
                "product_name": product_name,
                "product_price": product_price,
                "product_image": product_image,
                "product_quantity": product_quantity
            }

            cart_list.append(record)
        
        grand_total = total + shipping_cost
    else:
        total = 0
        shipping_cost = 0
        grand_total = 0

    return JsonResponse({
        'is_error': False, 
        'error_message': error_message,         
        'carts': cart_list,
        'total': '{:0,.2f}'.format(total),
        'shipping_cost': '{:0,.2f}'.format(shipping_cost),
        'grand_total': '{:0,.2f}'.format(grand_total),
        'number_of_items_in_cart': number_of_items_in_cart,        
    }) 




@csrf_exempt
def delete_item_from_cart(request):
    
    # กำหนดค่าเริ่มต้น
    username = request.user.username        
    is_error = True
    error_message = ""
    number_of_items_in_cart = 0    
    total = 0
    shipping_cost = 50
    grand_total = 0

    cart_list = []
    record = {}

    # รับค่า Item จากหน้า UI แล้วลบ
    item_id = request.POST.get('item_id')


    # เลือกว่าจะลบข้อมูลในตารางของ Memeber หรือ Visitor
    if username != "":
        order_item = MemberOrderItem.objects.get(id=item_id)
        order_item.delete()
    else:
        order_item = VisitorOrderItem.objects.get(id=item_id)
        order_item.delete()        

    # ส่งข้อมูล item ที่เหลือในตะกร้ากลับไปที่หน้า UI
    if not request.session.exists(request.session.session_key):
        number_of_items_in_cart = 0

        print("TODO 1")
    else:
        if username != "":
            print("TODO 2")
            session_key = request.session.session_key
            
            if 'order_id' in request.session:
                order_id = request.session.get('order_id')
                carts = MemberOrderItem.objects.filter(order_id=order_id).all()
            else:
                print("TODO 3")
                try:
                    order = MemberOrder.objects.filter(customer_id=request.user.id).filter(transaction_id=None).first()
                    print("ORDER : ", order)
                    if order:                        
                        carts = MemberOrder.objects.filter(memberorderitem__order_id=order.id).all()
                    else:
                        carts = []
                except ObjectDoesNotExist:
                    carts = []

            for item in carts:
                total = total + item.product.price

            grand_total = total + shipping_cost
            number_of_items_in_cart = len(carts)

        else:
            print("TODO 4")
            session_key = request.session.session_key            
            carts = VisitorOrderItem.objects.filter(session_id=session_key).all()
            number_of_items_in_cart = len(carts)

    
    if carts:
        total = 0
        grand_total = 0

        for item in carts:
            item_id = item.id
            product_name = item.product.product_name
            product_price = item.product.price
            product_image = item.product.image.url

            total = total + product_price
            
            record = {
                "item_id": item_id,
                "product_name": product_name,
                "product_price": product_price,
                "product_image": product_image,
            }

            cart_list.append(record)
        
        grand_total = total + shipping_cost
    else:
        total = 0
        shipping_cost = 0
        grand_total = 0

    return JsonResponse({
        'is_error': False, 
        'error_message': error_message,         
        'carts': cart_list,
        'total': '{:0,.2f}'.format(total),
        'shipping_cost': '{:0,.2f}'.format(shipping_cost),
        'grand_total': '{:0,.2f}'.format(grand_total),
        'number_of_items_in_cart': number_of_items_in_cart,        
    })    



@csrf_exempt
def add_to_cart(request):    
    
    product_id = request.POST.get('product_id')
    order_id = None

    is_error = True
    error_mesage = ""
    number_of_items_in_cart = 0
    username = request.user.username
    
    if username != "":
        print('username = ', username)

        is_error = True
        error_mesage = "TODO"
        number_of_items_in_cart = 0
        user_id = request.user.id

        # TODO
        try:
            print("ORDER ID x1 : ", request.session.get('order_id'))
            
            # เพิ่มข้อมูลลงตาราง Order       
            if 'order_id' in request.session:                            
                order_id = request.session.get('order_id')

                if order_id is None:
                    member_order = MemberOrder()
                    member_order.customer_id = user_id
                    member_order.date_ordered = date.today()
                    member_order.total = 0
                    member_order.save()
                    order_id = member_order.id
                    print("XXXXXXX : ", order_id)
                    request.session['order_id'] = order_id

                print("YYYYYY : ", order_id)
            else:
                member_order = MemberOrder()
                member_order.customer_id = user_id
                member_order.date_ordered = date.today()
                member_order.total = 0
                member_order.save()
                order_id = member_order.id
                print("XXXXXXX : ", order_id)
                request.session['order_id'] = order_id

            # เพิ่มข้อมูลลงตาราง OrderItem
            member_order_item = MemberOrderItem()
            member_order_item.product_id = product_id
            member_order_item.quantity = 1
            member_order_item.order_id = order_id
            member_order_item.save()
            cart = MemberOrderItem.objects.filter(order_id=order_id)
            number_of_items_in_cart = len(cart)
            

            is_error = False
        except Exception as e:
            is_error = True
            error_mesage = str(e)  

        print("ORDER ID xxx : ", order_id)      
    else:
        if not request.session.exists(request.session.session_key):
            request.session.create()
        
        session_key = request.session.session_key

        print("session_key = ", session_key)
        print('product_id = ', product_id)

        try:
            visitor_order_item = VisitorOrderItem()
            visitor_order_item.session_id = session_key
            visitor_order_item.product_id = product_id
            visitor_order_item.quantity = 1
            visitor_order_item.save()

            # นับจำนวนสินค้าที่เพิ่มในตะกร้า
            cart = VisitorOrderItem.objects.filter(session_id=session_key)
            number_of_items_in_cart = len(cart)

            is_error = False
        except Exception as e:
            is_error = True
            error_mesage = str(e)

    return JsonResponse({
        'is_error': is_error, 
        'error_message': error_mesage, 
        'number_of_items_in_cart': number_of_items_in_cart,
        'order_id': order_id

    })


@login_required
def custom_logout(request):
    logout(request)    
    return redirect("/")
