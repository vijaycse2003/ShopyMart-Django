from django.shortcuts import render,redirect
from .models import Product,Orders,OrderUpdate
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from math import ceil


def home(request):
    return render(request,'index.html')
def purchase(request):
    current_user=request.user
    print(current_user)
    allprods=[]
    catprods=Product.objects.values('category','id')
    cats={item['category'] for item in catprods}
    for cat in cats:
        prod=Product.objects.filter(category=cat)
        n=len(prod)
        nSlides=n//4 + ceil((n/4)-(n//4))
        allprods.append([prod,range(1,nSlides),nSlides])
    params={'allprods':allprods}
    return render(request,'purchase.html',params)

def check(request):
    if not request.user.is_authenticated:
        messages.warning(request,'Login and Try Again')
        return redirect('/shopauth/login')
    if request.method == "POST":
        items_json=request.POST.get('itemJson','')
        name=request.POST.get('name','')
        amount=request.POST.get('amt','')
        email=request.POST.get('email','')
        address1=request.POST.get('address1','')
        address2=request.POST.get('address2','')
        city=request.POST.get('city','')
        state=request.POST.get('state','')
        zip_code=request.POST.get('zip_code','')
        phone=request.POST.get('phone','')
        Order = Orders(items_json=items_json,name=name,amount=amount, email=email, address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone)
        print(amount)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,update_desc="the order has been placed")
        update.save()
        thank = True
    return render(request,'checkout.html')

def About(request):
    return render(request,'about.html')


def error404(request,exception):
    return render(request,"404.html")