'''
Created on Aug 14, 2012

@author: mbucknel
'''
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView

class CreateUserView(CreateView):
    form_class = UserCreationForm
    model = User
    
    def get_success_url(self):
        return self.request['next']
