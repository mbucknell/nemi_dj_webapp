'''
Created on Aug 14, 2012

@author: mbucknel
'''
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView

from forms import NEMIUserCreationForm

class CreateUserView(CreateView):
    ''' Extends CreateView using the NEMIUserCreationForm to create a user who can create and edit NEMI methods.
    Once a user has successfully created a new user, notifications are set to the emails on NEW_ACCOUNT_NOTIFICATIONS
    '''
    
    template_name='registration/create_user.html'
    form_class = NEMIUserCreationForm
    model = User
    
    def get_success_url(self):
        return reverse('nemi_create_account_success')
    
    def form_valid(self, form):
        self.object = form.save()
        
        #Send email to NEW_ACCOUNT_NOTIFICATIONS
        send_mail(subject="New NEMI user account created",
                  message="A new NEMI user account was created for %s (email: %s)" % (self.object.get_full_name(), self.object.email),
                  from_email="user_db@nemi.gov",
                  recipient_list=settings.NEW_ACCOUNT_NOTIFICATIONS)
        
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
        if user is not None:
            login(self.request, user)
        
        return HttpResponseRedirect(self.get_success_url())
    
    
class PasswordChangeView(FormView):
    '''Extends the FormView to use the django defined PasswordChangeForm to allow a logged in user 
    to change their password. The view will use the request parameter 'redirect_url' to determine where
    to redirect the view once the user successfully changes their password. This requires that "redirect_url" be saved
    using a "hidden" input element in the html form.
    '''
    
    template_name = 'registration/change_password.html'
    form_class = PasswordChangeForm
    
    def get_success_url(self):
        return self.request.POST['redirect_url']
    
    def get_form(self, form_class):
        return form_class(self.request.user, **self.get_form_kwargs()) 
    
    def get_context_data(self, **kwargs):
        context = super(PasswordChangeView, self).get_context_data(**kwargs)
        context['redirect_url'] = self.request.REQUEST['redirect_url']
        return context
    
    def form_valid(self, form):
        form.save()
        return super(PasswordChangeView, self).form_valid(form)
    
class MethodEntryView(TemplateView):
    template_name = 'method_entry.html'
    
    def get_context_data(self, **kwargs):
        context = super(MethodEntryView, self).get_context_data(**kwargs)
        context['apex_url'] = settings.APEX_METHOD_ENTRY_URL
        
        return context
    
    