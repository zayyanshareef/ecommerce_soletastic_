from django.contrib import admin
from django.urls import path
from .import views

urlpatterns = [
    path('',views.Dashboard,name = 'dashboard'),
    path('all_product',views.All_product,name = 'all_product'),
    path('view_product/<int:id>',views.View_product,name ='view_product'),
    path('user_profile/',views.User_Profile,name='user_profile'),
    path('edit_profile/<int:id>',views.Edit_profile,name="edit_profile"),
    path('address/',views.Address,name="address"),
    path('add_address/',views.Add_address,name="add_address"),
    path('delete_address/<int:id>',views.Delete_address,name="delete_address"),
    path('edit_address/',views.Edit_address,name="edit_address"),
    path('cart/',views.User_cart,name="user_cart"),
    path('add_to_cart/',views.Add_to_cart,name="add_to_cart"),
    path('delete_cart/<int:id>/', views.Delete_cart, name="delete_cart"),
    path('update-quantity/',views.update_quantity_view, name="update-quantity"),
    path('checkout/',views.Checkout,name="checkout"),
    path('edit_checkout_address/',views.Checkout_edit_address, name="edit_checkout_address"),
    path('checkout_add_address/',views.Checkout_add_address, name="checkout_add_address"),
    path('change_password/',views.Change_password,name="change_password"),
    path('user_order/',views.User_order,name='user_order'),
    path('confirmation/',views.Confirmation,name='confirmation'),
    path('download_invoice/<int:id>', views.download_invoice, name='download_invoice'),
    path('my_order/',views.My_Order,name="my_order"),
    path('order_details/<int:id>',views.Order_Details,name="order_details"),
    path('cancellation/<int:id>',views.Cancellation,name="cancellation"),
    path('pay_with_upi/',views.Pay_With_Upi,name="pay_with_upi"),
    path('add_wishlist/',views.Add_Wishlist,name="add_wishlist"),
    path('user_wishlist/',views.User_Wishlist,name="user_wishlist"),
    path('remove_wishlist/<int:id>',views.Remove_Wishlist,name="remove_wishlist"),
    path('my_wallet/',views.My_Wallet,name="my_wallet"),
    path("wallet_upi/",views.Wallet_upi,name="wallet_upi"),
    path("wallet_recharge/",views.wallet_Recharge,name="wallet_recharge"),
    path("return/<int:id>",views.Return,name="return"),
    
   
    
]
