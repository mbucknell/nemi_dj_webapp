
from django.forms import Form
from django.http import Http404, HttpResponse
from django.views.generic import View
from django.views.generic.edit import TemplateResponseMixin

from models import DefinitionsDOM
from utils.view_utils import xls_response, tsv_response

class ChoiceJsonView(View):
    ''' Extends the standard View to return a JSON object representing a list of choices
    '''
    def get_choices(self, request, *args, **kwargs):
        ''' Returns a list of tuples representing the choices. The first element in the tuple is the value
        and the second is the display value.
        '''
        
    def get(self, request, *args, **kwargs):
        choices = ['{"value" : "' + value + '", "display_value" : "' + display_value + '"}' 
                   for (value, display_value) in self.get_choices(request, *args, **kwargs)]
        
        return HttpResponse('{"choices" : [' + ','.join(choices) + ']}', mimetype='application/json')        
        
class FilterFormMixin(object):
    '''This mixin class is designed to process a form which sets query filter conditions.
    The method get_qs, should check the form's cleaned data and filter the query as appropriate and
    return the query set.
    The method, get_context_data, returns context data generated from the form.
    '''
    
    form_class = Form

    def get_qs(self, form):
        return None
    
    def get_context_data(self, form):
        return {}
                                     
class SearchResultView(View, TemplateResponseMixin):
    ''' This class extends the standard view and template response mixin. This class
    should be mixed with a class that provides a get_qs(form) method, get_context_data(form) method, and a form_class parameter.
    '''
    
    result_fields = () # Fields to be displayed on the results page
    result_field_order_by = '' #Field to order the query results. If null, no order is specified
    
    header_abbrev_set = () # The header definitions to retrieve from the DOM. These should be in the order (from left to right)
    # that they will appear on the screen
    
    def get_header_defs(self):
        ''' Returns a list of DefinitionsDOM objects matching the definition_abbrev using abbrev_set. 
        The objects will only have the definition_name and definition_description field set.
        The objects will be in the same order as abbrev_set and if an object is missing or there are multiple
        in the DefinitionsDOM table, then the name in abbrev_set is used with spaces replacing underscores and words
        capitalized with a standard description.
        '''
        def_qs = DefinitionsDOM.objects.filter(definition_abbrev__in=self.header_abbrev_set)
        
        header_defs = []
        for abbrev in self.header_abbrev_set:
            try:
                header_defs.append(def_qs.get(definition_abbrev=abbrev))
            except(DefinitionsDOM.MultipleObjectsReturned, DefinitionsDOM.DoesNotExist):
                header_defs.append(DefinitionsDOM(definition_name=abbrev.replace('_', ' ').title(),
                                                  definition_description='')) 
            
        return header_defs

    def get_values_qs(self, qs):
        ''' Returns the qs as a values query set with result_fields in the set and ordered by result_field_order_by.'''
        v_qs = qs.values(*self.result_fields).distinct()
        if self.result_field_order_by:
            v_qs = v_qs.order_by(self.result_field_order_by)
            
        return v_qs
    
    def get_results_context(self, qs):
        '''Returns a dictionary containing the query set results. By default this returns self.get_values_qs() as the 'results' key.
        If you need to process the values query set further or generate additional information from the query set, override this method.
        '''
        return {'results': self.get_values_qs(qs)}

    def get(self, request, *args, **kwargs):
        '''Process the GET request.'''
        if request.GET:
            form = self.form_class(request.GET)
            if form.is_valid():
                context = {'search_form' : form,
                           'query_string' : '?' + request.get_full_path().split('?', 1)[1],
                           'header_defs' : self.get_header_defs(),
                           'hide_search' : True,
                           'show_results' : True}
                context.update(self.get_context_data(form))
                context.update(self.get_results_context(self.get_qs(form)))
                
                return self.render_to_response(context)          
             
            else:
                return self.render_to_response({'search_form' : form,
                                        'hide_search' : False,
                                        'show_results' : False}) 
            
        else:
            return self.render_to_response({'search_form' : self.form_class(),
                                            'hide_search' : False,
                                            'show_results' : False})
            

class ExportSearchView(View):
    ''' Extends the standard View to implement the view which exports the search results
    table. This should be extended along with the FilterFormMixin.
    '''

    export_fields = () # Fields in the query set to be exported to file
    export_field_order_by = '' # Field name to order the export query results by. If null, no order is specified
    filename = '' #Provide the name of the file to create. The appropriate suffix will be added to the filename
    
    def get_export_qs(self, qs):
        ''' Return a values list query set from the objects query set using export_fields to select fields
        and export_field_order_by to order the query set.
        '''
        export_qs = qs.values_list(*self.export_fields).distinct()
        if self.export_field_order_by:
            export_qs = export_qs.order_by(self.export_field_order_by)
            
        return export_qs
    

    def get(self, request, *args, **kwargs):
        '''Processes the get request.'''
        if request.GET:
            form = self.form_class(request.GET)
            if form.is_valid():
                HEADINGS = [name.replace('_', ' ').title() for name in self.export_fields]
                export_type = kwargs.get('export', '')
                
                if export_type == 'tsv':
                    return tsv_response(HEADINGS, self.get_export_qs(self.get_qs(form)), self.filename)
                
                elif export_type == 'xls':
                    return xls_response(HEADINGS, self.get_export_qs(self.get_qs(form)), self.filename)
                
                else:
                    raise Http404
            
            else:
                raise Http404
            
        else:
            raise Http404
                