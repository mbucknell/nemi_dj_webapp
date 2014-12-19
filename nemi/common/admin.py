
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.forms import ModelForm

from tinymce.widgets import TinyMCE

class FlatPageForm(ModelForm):
    
    class Meta:
        model = FlatPage
        fields = '__all__'
        widgets = {'content' : TinyMCE(attrs={'cols' : 100, 
                                              'rows': 50,
                                              })
                   }
        
class FlatPageAdmin(admin.ModelAdmin):
    
    form = FlatPageForm
    
    
admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)

