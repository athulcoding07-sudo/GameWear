from django import forms
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSignupForm(forms.ModelForm):

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password"})
    )

    referral_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Referral Code"})
    )

    class Meta:
        model = User
        fields = ["full_name", "email", "phone_number"]

        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "9876543210"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 apply SAME design to ALL fields
        common_classes = (
            "w-full px-4 py-3 bg-neutral-800 border border-neutral-700 "
            "rounded-lg focus:ring-2 focus:ring-white text-white"
        )

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", common_classes)
    # ---------- FIELD VALIDATIONS ----------

    def clean_email(self):
        email = self.cleaned_data.get("email").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")

        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")

        if phone and User.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")

        return phone

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match")

        return cleaned_data

    # ---------- SAVE METHOD ----------

    def save(self, commit=True):
        user = super().save(commit=False)

        # 🔐 set password correctly
        user.set_password(self.cleaned_data["password1"])

        # referral handling (optional)
        code = self.cleaned_data.get("referral_code")
        if code:
            try:
                user.referred_by = User.objects.get(referral_code=code)
            except User.DoesNotExist:
                self.add_error("referral_code", "Invalid referral code")

        if commit:
            user.save()

        return user
class UserEditProfileForm(forms.ModelForm):

   
    class Meta:
        model = User
        fields = ["full_name",  "phone_number", "dob", "gender","profile_image"]
        widgets = {
            "dob": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "w-full bg-black border border-neutral-800 rounded-xl px-4 py-4 text-sm text-white focus:border-white focus:outline-none transition",
                }
            )
        }

    #     widgets = {
    #         "full_name": forms.TextInput(attrs={"placeholder": "Full name"}),
    #         "email": forms.EmailInput(attrs={"placeholder": "Email address"}),
    #         "phone_number": forms.TextInput(attrs={"placeholder": "Phone number"}),
    #         "dob": forms.DateInput(
    #             attrs={
    #                 "type": "date",
    #                 "placeholder": "Date of birth",
    #             }
    #         ),
    #         "gender": forms.Select(),
    #     }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     common_classes = (
    #         "w-full px-4 py-3 bg-neutral-800 border border-neutral-700 "
    #         "rounded-lg focus:ring-2 focus:ring-white text-white"
    #     )

    #     for field in self.fields.values():
    #         field.widget.attrs.setdefault("class", common_classes)

    # ---------- VALIDATIONS ----------

    

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")

        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")

        if User.objects.filter(phone_number=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This phone number is already in use.")

        return phone

    def clean_dob(self):
        dob = self.cleaned_data.get("dob")

        if dob is None:
            return dob

        from datetime import date

        if dob > date.today():
            raise forms.ValidationError("Date of birth cannot be in the future.")

        return dob