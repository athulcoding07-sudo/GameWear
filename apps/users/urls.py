"""
Docstring for gamewear.apps.users.urls
"""
from django.urls import path
from .views import login_view,signup_view,user_dashboard,verify_signup_otp,resend_signup_otp


app_name = "users"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("dashboard/",user_dashboard,name="dashboard"),
    path("verify-signup-otp/", verify_signup_otp, name="verify_signup_otp"),
    path("resend-signup-otp/", resend_signup_otp, name="resend_signup_otp"),




]
