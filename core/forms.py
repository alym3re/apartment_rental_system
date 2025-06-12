from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Application, Payment, Message, Announcement, LeaveRequest
from .models import *



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    facebook_account = forms.URLField(required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    occupation = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 
                 'first_name', 'last_name', 'phone_number', 
                 'facebook_account', 'address', 'occupation']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 
                 'facebook_account', 'address', 'occupation', 'profile_picture']

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['full_name', 'address', 'contact_number', 'email', 
                 'facebook_account', 'occupation', 'number_of_people']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class PaymentForm(forms.ModelForm):
    mode_of_payment = forms.ChoiceField(
        choices=Payment.PAYMENT_MODE_CHOICES,
        widget=forms.RadioSelect,
        initial=Payment.CASH
    )
    
    class Meta:
        model = Payment
        fields = ['amount', 'payment_date', 'mode_of_payment', 'receipt', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class ConversationForm(forms.ModelForm):
    subject = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    class Meta:
        model = Conversation
        fields = ['subject', 'participants']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['participants'].queryset = User.objects.exclude(id=user.id)
        else:
            self.fields['participants'].queryset = User.objects.all()

class MessageForm(forms.ModelForm):
    conversation = forms.ModelChoiceField(
        queryset=Conversation.objects.all(),
        required=False,
        widget=forms.HiddenInput()
    )
    class Meta:
        model = Message
        fields = ['conversation', 'recipient', 'subject', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        # If 'conversation' is passed, hide recipient and subject fields
        conversation = kwargs.get('initial', {}).get('conversation') or kwargs.get('instance', None) and getattr(kwargs['instance'], 'conversation', None)
        super().__init__(*args, **kwargs)
        if conversation:
            self.fields['recipient'].widget = forms.HiddenInput()
            self.fields['subject'].widget = forms.HiddenInput()
            self.fields['recipient'].required = False
            self.fields['subject'].required = False

class AnnouncementForm(forms.ModelForm):
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role=User.TENANT),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Announcement
        fields = ['title', 'content', 'is_global', 'recipients']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['reason', 'requested_end_date']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 5}),
            'requested_end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = [
            'name', 'description', 'monthly_price', 'location',
            'payment_inclusions', 'house_rules', 'main_image'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'payment_inclusions': forms.Textarea(attrs={'rows': 2}),
            'house_rules': forms.Textarea(attrs={'rows': 2}),
        }