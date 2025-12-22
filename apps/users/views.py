from django.shortcuts import render,redirect
from django.contrib import messages
from django.db import IntegrityError
from .forms import UserSignupForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.otp.services import send_otp,verify_otp,resend_otp


# Create your views here.

def login_view(request):
    """  
    Handles user login.

    Display the login page
    check it is post request,authenticate,admin or user
    if admin go to admin dashboard and user go to user dashboard

    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # authenticate user
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful")

            # ADMIN
            if user.is_staff or user.role == "admin":
                return redirect("adminpanel:dashboard")

            # NORMAL USER
            return redirect("users:dashboard")

        else:
            messages.error(request, "Invalid email or password")

    return render(request, "users/login.html")

User = get_user_model()


def signup_view(request):
    """
    Handles user registration with Email OTP verification.

    - GET  → Display signup form
    - POST → Validate form, create inactive user, send OTP, redirect to OTP verify
    """

    if request.method == "POST":
        form = UserSignupForm(request.POST)

        try:
            if form.is_valid():
                # Create user but do NOT activate yet
                user = form.save(commit=False)
                user.is_active = False
                user.save()

               
                # Send OTP email
                send_otp(user, "signup")

                # Store user id in session for OTP verification
                request.session["signup_user_id"] = user.id

                messages.success(request, "OTP sent to your email. Please verify.")
                return redirect("users:verify_otp")

            else:
                messages.error(request, "Please correct the errors below.")

        except IntegrityError:
            messages.error(
                request,
                "A user with this email or phone already exists."
            )

        except Exception:
            messages.error(
                request,
                "Something went wrong. Please try again later."
            )

    else:
        form = UserSignupForm()

    return render(request, "users/signup.html", {"form": form})





@login_required
def user_dashboard(request):
    """
    - show the user dashboard
    -
    """
    return render(request, "users/dashboard.html")



User = get_user_model()


def verify_signup_otp(request):
    """
    Verify signup OTP and activate user account
    """

    user_id = request.session.get("signup_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("users:signup")

    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        entered_otp = request.POST.get("otp")

        success, message = verify_otp(user, "signup", entered_otp)

        if success:
            user.is_active = True
            user.save(update_fields=["is_active"])

            # cleanup session
            request.session.pop("signup_user_id", None)

            messages.success(request, "Account verified successfully. Please log in.")
            return redirect("users:login")

        messages.error(request, message)

    return render(request, "users/verify_signup_otp.html")



    
def resend_signup_otp(request):
    """
    Resend signup OTP
    - get the id and checke it 
    - then we provide there resent the otp
    """

    user_id = request.session.get("signup_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect("users:signup")

    user = get_object_or_404(User, id=user_id)

    success, message = resend_otp(user, "signup")
    messages.info(request, message)

    return redirect("users:verify_signup_otp")
