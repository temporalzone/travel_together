from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TravelGroup, Chat, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email Address')
    phone_number = forms.CharField(max_length=15, required=True, label='Phone Number (e.g., +1234567890)')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username already exists. Choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email already exists. Use another.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if UserProfile.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("This phone number already exists. Try another.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user, 
                phone_number=self.cleaned_data['phone_number']
            )
        return user

class GroupForm(forms.ModelForm):
    class Meta:
        model = TravelGroup
        fields = ['name', 'description', 'group_type', 'is_public', 'image']  # Add 'image'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'group_type': forms.Select(choices=TravelGroup._meta.get_field('group_type').choices),
            'is_public': forms.CheckboxInput(),
        }

class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Share your trek tips or questions...'}),
        }