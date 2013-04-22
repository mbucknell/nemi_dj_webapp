
from django.forms import Form

from .models import HelpContent

class BaseDefinitionsForm(Form):
    ''' Extends Form and adds attributes retrieved from WebFormDefinitions model.
    '''
    
    def __init__(self, *args, **kwargs):
        super(BaseDefinitionsForm, self).__init__(*args, **kwargs)
        # For each form field, retrieve the corresponding WebFormDefinition object
        # and fill in the appropriate attribute.
        for f in self.fields:
            try:
                field_def = HelpContent.objects.get(field_name=f)
            except(HelpContent.DoesNotExist):
                continue
            
            if field_def.label:
                self.fields[f].label = field_def.label
            if field_def.tooltip:
                self.fields[f].tooltip = field_def.tooltip
            if field_def.description:
                self.fields[f].help_text = field_def.description