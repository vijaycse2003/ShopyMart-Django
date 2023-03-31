
from django.urls import path
from Shopauth import views as v
urlpatterns = [ 
    path('signup',v.Signup,name='signup'),
    path('login',v.Handlelogin,name='login'),
    path('logout',v.Handlelogout,name='logout'),
    path('activate/<uidb64>/<token>',v.ActivateAcountView.as_view(),name='activate'),
    path('request-reset-email',v.RequestResetEmailView.as_view(),name='reset'),
    path('set-new-password/<uidb64>/<token>',v.SetNewPasswordView.as_view(),name='set-new-password'),
]
 