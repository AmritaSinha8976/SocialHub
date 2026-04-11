from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class EmailOTPRequestForm(forms.Form):
    """Step 1 — enter email + basic info, receive OTP."""
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First name'}))
    last_name  = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last name (optional)'}))
    username   = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Choose a username'}))
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'your@email.com'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username


class OTPVerifyForm(forms.Form):
    """Step 2 — enter the 6-digit OTP."""
    otp = forms.CharField(
        max_length=6, min_length=6,
        widget=forms.TextInput(attrs={
            'class':'form-control otp-input',
            'placeholder':'000000',
            'maxlength':'6',
            'inputmode':'numeric',
            'autocomplete':'one-time-code',
        })
    )


class SetPasswordForm(forms.Form):
    """Step 3 — set password after OTP verified."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Create a password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm password'})
    )

    def clean(self):
        cd = super().clean()
        if cd.get('password1') != cd.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        if len(cd.get('password1','')) < 8:
            raise forms.ValidationError('Password must be at least 8 characters.')
        return cd


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class':'form-control','placeholder':'Username'})
        self.fields['password'].widget.attrs.update({'class':'form-control','placeholder':'Password'})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = Profile
        fields = ['profile_picture','bio','website','location','is_private']
        widgets = {
            'bio':       forms.Textarea(attrs={'class':'form-control','rows':4,'placeholder':'Tell people about yourself...'}),
            'website':   forms.URLInput(attrs={'class':'form-control','placeholder':'https://'}),
            'location':  forms.TextInput(attrs={'class':'form-control','placeholder':'City, Country'}),
            'profile_picture': forms.FileInput(attrs={'class':'form-control','accept':'image/*'}),
            'is_private': forms.CheckboxInput(attrs={'class':'form-check-input'}),
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    class Meta:
        model  = User
        fields = ['first_name','last_name','email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class':'form-control'}),
            'last_name':  forms.TextInput(attrs={'class':'form-control'}),
        }
