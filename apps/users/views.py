from django.shortcuts import render,redirect
from django.contrib import messages
from django.db import IntegrityError
from .forms import UserSignupForm,UserEditProfileForm,EmailChangeForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.shortcuts import get_object_or_404
from apps.otp.services import send_otp,verify_otp,resend_otp
from django.contrib.auth import update_session_auth_hash
from .models import PendingEmail



# Create your views here.



User = get_user_model()


def signup_view(request):
    """
    Handles user registration with Email OTP verification.

    - GET  → Display signup form
    - POST → Validate form, create inactive user, send OTP, redirect to OTP verify
    """
    
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        print('hi ...')
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
                return redirect("users:verify_signup_otp")
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



def forgot_password_view(request):
    """
    - show the email input form
    - get email,sent otp,redirect to  otp verify page
    """
    if request.method == "POST":
       
            
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            send_otp(user,"reset_password")
            request.session['reset_user_id'] = user.id
            messages.success(request,"OTP sent to your email.")
            return redirect("users:verify_reset_otp")
        except User.DoesNotExist:
            messages.error(request,"No account found with this email.")

        except Exception:
            messages.error(request,"Something went wrong. Please try again later.")

    return render(request,"users/forgot_password.html")

def verify_reset_otp(request):
    """
    verify otp for password reset
    """
    user_id = request.session['reset_user_id']
    if not user_id:
        messages.error(request,"Session expired. Please try again.")
        return redirect("users:forgot_password")
    user = get_object_or_404(User, id = user_id)
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        success,message = verify_otp(user,'reset_password',entered_otp)
        if success:
            messages.success(request, "OTP verified. Set a new password.")
            return redirect("users:reset_password")
        messages.error(request, message)

    return render(request,'users/verify_reset_otp.html')


def resend_reset_otp(request):
    """
    - resend the otp
    - check the user_id
    - comform user exist then send the otp
    """
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please try again.")
        return redirect("users:forgot_password")
    user = get_object_or_404(User,id = user_id)
    success, message = resend_otp(user, "reset_password")
    messages.info(request, message)

    return redirect("users:verify_reset_otp")



def reset_password_view(request):
    """
    - reset password

    """
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please try again.")
        return redirect("users:forgot_password")
    user = get_object_or_404(User,id = user_id)
    


    if request.method == "POST":
        
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        print(f'{password1},{password2}')

        if not password1 or not password2:
            messages.error(request, "All fields are required.")
        elif password1 != password2:
            messages.error(request, "Passwords do not match.") 
        else:
            user.password = make_password(password1)
            user.save(update_fields=["password"])
            # cleanup session
            request.session.pop("reset_user_id", None)
            messages.success(request, "Password reset successful. Please log in.")
            return redirect("users:login") 
    return render(request,'users/reset_password.html',{"validlink": True})


@login_required
def user_dashboard(request):
    """
    - show the user dashboard
    
    """
    return render(request, "users/dashboard.html")

@login_required
def user_profile_view(request):
    """
    - show the user profile
    """

    return render(request, "users/profile/profile_view.html")

@login_required
def user_profile_edit_view(request):
    if request.method == "POST":
        
        form = UserEditProfileForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("users:user_profile_edit")
        else:
            print(form.errors)
    else:
        form = UserEditProfileForm(instance=request.user)

    return render(request, "users/profile/edit_profile.html", {"form": form})




@login_required
def user_update_password_view(request):
    """
    Allow logged-in user to update their password.
    - Verifies old password
    - Confirms new password match
    - Keeps user logged in after change
    """

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        # 1️⃣ Validate fields
        if not old_password or not new_password1 or not new_password2:
            messages.error(request, "All fields are required.")
            return redirect("users:user_profile_edit")

        # 2️⃣ Check old password
        if not request.user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("users:user_profile_edit")

        # 3️⃣ Check new password match
        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect("users:user_profile_edit")

        # 4️⃣ Set new password
        request.user.set_password(new_password1)
        request.user.save()

        # 5️⃣ Keep user logged in
        update_session_auth_hash(request, request.user)

        messages.success(request, "Password updated successfully.")
        return redirect("users:user_profile")

    return render(request, "users/update_password.html")



@login_required
def request_email_change_sent_otp(request):
    if request.method == "POST":
        form = EmailChangeForm(request.POST, user=request.user)  # ✅ FIX

        if form.is_valid():
            new_email = form.cleaned_data["new_email"]

            PendingEmail.objects.update_or_create(
                user=request.user,
                defaults={"new_email": new_email}
            )

            send_otp(
                user=request.user,
                purpose="email_change",
                email=new_email
            )

            request.session["email_change"] = True
            messages.success(request, "OTP sent to new email.")
            return redirect("users:verify_email_change_otp")

        

    else:
        form = EmailChangeForm(user=request.user)  # ✅ also pass user on GET

    return render(
        request,
        "users/profile/email_view.html",
        {"form": form}
    )

@login_required
def verify_email_change_otp(request):
    if not request.session.get("email_change"):
        return redirect("users:user_profile_edit")

    if request.method == "POST":
        otp = request.POST.get("otp")

        # Reuse existing verification logic
        if verify_otp(
            user=request.user,
            purpose="email_change",
            code=otp
        ):
            pending = PendingEmail.objects.get(user=request.user)

            # Update real email ONLY now
            request.user.email = pending.new_email
            request.user.save(update_fields=["email"])

            pending.delete()
            request.session.pop("email_change")

            messages.success(request, "Email updated successfully.")
            return redirect("users:user_profile_edit")

        messages.error(request, "Invalid or expired OTP.")

    return render(request, "users/profile/verify_email_otp.html")

@login_required
def resend_email_change_otp(request):
    """
    - resend email change otp
    - confirm session exists
    - confirm pending email exists
    - resend otp to NEW email
    """

    if not request.session.get("email_change"):
        messages.error(request, "Session expired. Please try again.")
        return redirect("users:user_profile_edit")

    try:
        pending = PendingEmail.objects.get(user=request.user)
    except PendingEmail.DoesNotExist:
        messages.error(request, "No pending email change found.")
        return redirect("users:user_profile_edit")

    # Reuse your existing resend_otp logic
    success, message = resend_otp(
        user=request.user,
        purpose="email_change",
        email=pending.new_email   # IMPORTANT
    )

    messages.info(request, message)
    return redirect("users:verify_email_change_otp")



    

