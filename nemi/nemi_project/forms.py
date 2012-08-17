'''
Created on Aug 15, 2012

@author: mbucknel
'''
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class NEMIUserCreationForm(UserCreationForm):
    '''Extends the UserCreationForm to add the first_name, last_name, and email field
    which are required for NEMI logins. Extend the save command to save these fields
    and set is_active to True and add the user automatically to the nemi_data_entry group
    '''
    
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super(NEMIUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = "30 characters or fewer. Letters, digits and @/./+/-/_ only." 
        
    def save(self, commit=True):
        user = super(NEMIUserCreationForm, self).save(commit=False)

        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.is_active = True

        if commit:
            user.save()
            
        user.groups.add(Group.objects.get(name="nemi_data_entry"))

        return user
        