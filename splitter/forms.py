from django import forms
from django.contrib.auth.forms import UserCreationForm
from splitter.models import User,group,group_members,transaction,debt

class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta():
        model = User
        fields = ['username','email','password1','password2']

class GroupForm(forms.ModelForm):
    class Meta():
        model = group
        fields = ['name']
