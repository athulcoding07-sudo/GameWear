"""
Docstring for gamewear.apps.users.urls
"""
from django.urls import path
from .views import (
    login_view,
    signup_view,
    user_dashboard,
    verify_signup_otp,
    resend_signup_otp,
    forgot_password_view,
    verify_reset_otp,
    resend_reset_otp,
    reset_password_view,
    user_profile_view,
    user_profile_edit_view,
    user_update_password_view
    
)
#from .views import login_view,signup_view,user_dashboard,verify_signup_otp,resend_signup_otp,forgot_password_view,verify_reset_otp


app_name = "users"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("signup/", signup_view, name="signup"),
    path("dashboard/",user_dashboard,name="dashboard"),
    path("verify-signup-otp/", verify_signup_otp, name="verify_signup_otp"),
    path("resend-signup-otp/", resend_signup_otp, name="resend_signup_otp"),
    path("forgot-password/", forgot_password_view, name="forgot_password"),
    path("verify-reset-otp/", verify_reset_otp, name="verify_reset_otp"),
    path("resend-reset-otp/", resend_reset_otp, name="resend_reset_otp"),
    path("reset-password/", reset_password_view, name="reset_password"),
    path("user-profile/",user_profile_view, name="user_profile"),
    path("user-profile-edit/",user_profile_edit_view, name="user_profile_edit"),
    path("user-update-password/",user_update_password_view, name="user_update_password"),


]
