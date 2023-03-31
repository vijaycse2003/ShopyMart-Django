from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.views.generic import View

#Activate the user account
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.urls import NoReverseMatch,reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes,DjangoUnicodeDecodeError
from django.utils.encoding import force_str

#Token will allow amd Create Random Token id
from .utils import TokenGenerator,generate_token
#password generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
#Emails
from django.core.mail import send_mail,EmailMultiAlternatives,BadHeaderError
from django.conf import settings
from django.core import mail
from django.core.mail import EmailMessage

#Threading
import threading

class EmailThread(threading.Thread):
    def __init__(self,email_message):
        self.email_message=email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


def Signup(request):
    if request.method == "POST":
        email=request.POST['email']
        password=request.POST['pass']
        confirm_password=request.POST['cpass']
        if password!=confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'Auth/signup.html')

        try:
            if User.objects.get(username=email):
                messages.warning(request,"Email is Taken")
                return render(request,'Auth/signup.html')

        except Exception as identifer:
            pass

        user=User.objects.create_user(email,email,password)
        print(user)
        user.save()
        user.is_active=False
        current_site=get_current_site(request)
        email_subject="Activate Your Account"
       
        message=render_to_string('Auth/activate.html',{
            'user':user,
            'domain':'127.0.0.1:8000',
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':generate_token.make_token(user)
        })

        # send_mail(email_subject,message,settings.EMAIL_HOST_USER,[email],)
        email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email],)
        EmailThread(email_message).start()
        messages.info(request,'Activate Your Account By Clicking Link On Your Email')
        return redirect('/shopauth/login')

    return render(request,'Auth/signup.html')

class ActivateAcountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        
        except Exception as identifer:
            user=None
            print('error',identifer)

        if user is not None and generate_token.check_token(user,token): 
            user.is_active=True
            user.save()
            messages.info(request,"Account Activated Successfully")
            return redirect('/shopauth/login')
        return render(request,'Auth/activatefail.html')
    

def Handlelogin(request):
    if request.method == "POST":
        username=request.POST['email']
        userpassword=request.POST['password']
        myuser=authenticate(username=username,password=userpassword)

        if myuser is not None:
            login(request,myuser)
            messages.success(request,"Login Successs")
            return render(request,'index.html')

        else:
           messages.error(request,"Invalid Crediential")
           return redirect('/shopauth/login')
    return render(request,'Auth/Login.html') 
     

def Handlelogout(request):
    logout(request)
    messages.success(request,"Logout Success")
    return redirect('/shopauth/login')

class RequestResetEmailView(View):
    def get(self,request):
        return render(request,'Auth/Request-Reset-Email.html')

    def post(self,request):
        email=request.POST['email']
        user=User.objects.filter(email=email)

        if user.exists():
            current_site=get_current_site(request)
            email_subject="[Reset Your Password]"
            message=render_to_string('Auth/reset-user-password.html',{
                 'domain':'127.0.0.1:8000',
                 'uid':urlsafe_base64_encode(force_bytes(user[0].pk)),
                 'token':PasswordResetTokenGenerator().make_token(user[0])
               })

#Email send information
            email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])

#This is fastest Threading method call
            EmailThread(email_message).start()

            messages.info(request,"We Have Sent You An Email With Instruction On How To Reset The Password")
            return render(request,'Auth/request-reset-email.html')


class SetNewPasswordView(View):
    def get(self,request,uidb64,token):

        context={
            'uidb64':uidb64,
            'token':token,
        }
        try:
            user_id=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=user_id)

            if  not PasswordResetTokenGenerator().check_token(user,token):
                messages.warning(request,"Password Reset Link is Invalid")
                return render(request,'Auth/request-reset-email.html')

        except DjangoUnicodeDecodeError as identifier:
            pass 

        return render(request,'Auth/set-new-password.html',context)

    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token,
        }

        if request.method == 'POST':
            password=request.POST['pass']
            cpassword=request.POST['pass1']

            if password!=cpassword:
                messages.warning(request,"Password is Not Matching")
                return render(request,"Auth/set-new-password.html",context)

            try:
                user_id=force_str(urlsafe_base64_decode(uidb64))
                user=User.objects.get(pk=user_id)
                user.set_password(password)
                user.save()
                messages.success(request,"Password Reset Success Please Login With NewPassword")
                return redirect('/Auth/login')

            except DjangoUnicodeDecodeError as identifier:
                messages.error(request,"Something went Wrong")
                return render(request,"Auth/set-new-password.html",context)
            
        return render(request,"Auth/set-new-password.html",context)