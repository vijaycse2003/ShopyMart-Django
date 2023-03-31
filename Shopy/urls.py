from django.urls import path
from Shopy import views as v
urlpatterns = [ 
    path('',v.home,name='home'),
    path('purchase',v.purchase,name='purchase'),
    path('check',v.check,name='check'),
    path('about',v.About,name='about'),
]
