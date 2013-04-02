
from django.contrib import admin
from django.forms import ModelForm

from tinymce.widgets import TinyMCE

from .models import HelpContent

class HelpContentForm(ModelForm):
    '''Extends ModelForm to use the TinyMCE editor (WYSIWYG) for the description field
    '''
    
    class Meta:
        model = HelpContent
        widgets = {'description' : TinyMCE(attrs={'cols' : 100, 'rows': 10},
                                           mce_attrs={
                                             'theme_advanced_buttons1' : "bold,italic,underline,strikethrough,link,unlink,sub,sup,bullist,numlist",
                                             'theme_advanced_statusbar_location' : "none"  
                                           })
                   }
        

class HelpContentAdmin(admin.ModelAdmin):

    form = HelpContentForm
    
    list_display = ('field_name', 'label')
    
    
admin.site.register(HelpContent, HelpContentAdmin)