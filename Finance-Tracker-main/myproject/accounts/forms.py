from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
# accounts/forms.py

from django import forms
from .models import FinancialItem, UserProfile



class RemoveItemForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.HiddenInput)

# accounts/forms.py

from django import forms
from .models import FinancialItem

class AddItemForm(forms.ModelForm):
    class Meta:
        model = FinancialItem
        fields = ['name', 'cost', 'month', 'year', 'tag']  # Include 'tag'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'].widget = forms.Select(choices=[(i, i) for i in range(1, 13)])  # Select field for month
        self.fields['year'].widget = forms.Select(choices=[(i, i) for i in range(2020, 2031)])  # Select field for year
class SetBudgetForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['monthly_budget']