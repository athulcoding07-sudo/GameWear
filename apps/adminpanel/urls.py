from django.urls import path
from .views import admin_dashboard,customers_view,customers_list,logout_view,add_user,edit_user,block_user,unblock_user


app_name = "adminpanel" 

urlpatterns = [
    path("dashboard/",admin_dashboard,name='dashboard'),
    path("customer-view/<int:customer_id>/",customers_view,name='customers_view'),
    path("customer-list/",customers_list,name='customers_list'),
    path("logout/", logout_view, name="logout_view"),
    path("add-user/", add_user, name="add_user"),
    path("edit-user/", edit_user, name="edit_user"),
    path("customers/block/<int:user_id>/", block_user, name="block_user"),
    path("customers/unblock/<int:user_id>/", unblock_user, name="unblock_user"),


    
]
