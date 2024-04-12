from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    # ................User Authentications.....................


    path('login/',views.Login,name ='login'),
    path('signup/',views.Signup,name="signup"),
    path('signupotp/',views.Signupotp,name='signupotp'),
    path('logout/',views.Logout,name='logout'),



    # .........................end..........................

    #/////////////////////////// forgot password ///////////////////



    path('forgot_password/',views.Forgot_password,name='forgot_password'),
    path('forget_OTP_check/',views.Forget_OTP_check,name='forget_OTP_check'),
    path('new_password/',views.New_password,name='new_password'),
]
