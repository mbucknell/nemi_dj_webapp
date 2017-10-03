'''
Created on Aug 14, 2012

@author: mbucknel
'''
import json

from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView

from domhelp.views import FieldHelpMixin
from newsfeed.views import RecentNewsMixin

from . import __version__
from .forms import NEMIUserCreationForm


class CreateUserView(CreateView):
    ''' Extends CreateView using the NEMIUserCreationForm to create a user who can create and edit NEMI methods.
    Once a user has successfully created a new user, notifications are set to the emails on NEW_ACCOUNT_NOTIFICATIONS
    '''

    template_name = 'registration/create_user.html'
    form_class = NEMIUserCreationForm
    model = User

    def get_success_url(self):
        #pylint: disable=R0201
        return reverse('nemi_create_account_success')

    def form_valid(self, form):
        #pylint: disable=W0201
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


class PasswordChangeView(LoginRequiredMixin, FormView):
    '''Extends the FormView to use the django defined PasswordChangeForm to allow a logged in user
    to change their password. The view will use the request parameter 'redirect_url' to determine where
    to redirect the view once the user successfully changes their password. This requires that "redirect_url" be saved
    using a "hidden" input element in the html form.
    '''

    template_name = 'registration/change_password.html'
    form_class = PasswordChangeForm

    def get_success_url(self):
        return self.request.POST['redirect_url']

    def get_form(self, form_class=PasswordChangeForm):
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super(PasswordChangeView, self).get_context_data(**kwargs)
        context['redirect_url'] = self.request.GET.get('redirect_url') or reverse('home')
        return context

    def form_valid(self, form):
        form.save()
        return super(PasswordChangeView, self).form_valid(form)


class HomeView(RecentNewsMixin, FieldHelpMixin, TemplateView):
    template_name = 'home.html'

    field_names = ['analysis_types',
                   'design_objectives',
                   'item_type',
                   'sam_complexity',
                   'sponser_types',
                   'media_emphasized',
                   'special_topics']


class MethodEntryView(TemplateView):
    template_name = 'method_entry.html'


def version(request):
    return HttpResponse(json.dumps({
        'version': __version__
    }), content_type='application/json')
