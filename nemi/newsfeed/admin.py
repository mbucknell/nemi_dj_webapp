
from django.contrib import admin
from django.forms import ModelForm
from django.utils.html import format_html

from tinymce.widgets import TinyMCE

from .models import NewsItem


class NewsItemForm(ModelForm):
    
    class Meta:
        model = NewsItem
        widgets = {'headline' : TinyMCE(attrs={'cols': 40, 'rows': 4},
                                        mce_attrs={
                                            'theme_advanced_buttons1' : "bold, italic,underline,strikethrough,link,unlink,sub,sup",
                                            'theme_advanced_statusbar_location': "none"
                                        })}


class NewsItemAdmin(admin.ModelAdmin):
    form = NewsItemForm
    
    def headline_display(self, obj):
        return format_html(obj.headline);
    headline_display.allow_tags = True

    list_display = ('headline_display', 'created', )
    
    
admin.site.register(NewsItem, NewsItemAdmin)
