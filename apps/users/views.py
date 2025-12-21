from django.shortcuts import render,redirect
from django.contrib import messages
from django.db import IntegrityError
from .forms import UserSignupForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required




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


def signup_view(request):
    """
    Handles user registration.

    display the signup page  GET
    and valideat -
    if sucsess go to login page


    """
    if request.method == "POST":


        form = UserSignupForm(request.POST)

        try:
            if form.is_valid():
                form.save()
                messages.success(request, "Account created successfully. Please log in.")
                return redirect("users:login")
            else:
                messages.error(request, "Please correct the errors below.")

        except IntegrityError:
                # Database-level failure (rare but possible)
            messages.error(
                    request,
                    "Something went wrong. Please try again later"
            )



        # except Exception:
        #     # Catch any unexpected error
        #     messages.error(
        #         request,
        #         "Something went wrong. Please try again later."
        #     )

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