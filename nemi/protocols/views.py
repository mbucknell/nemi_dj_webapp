
from django.http import HttpResponse
from django.views.generic import View, ListView, DetailView

from common.models import SourceCitationRef


class ProtocolCountView(View):
    '''
    Extends the standard View to retrieve and return as a json object the total number of protocols in the datastore.
    '''

    def get(self, request, *args, **kwargs):
        return HttpResponse('{"protocol_count" : "' + str(SourceCitationRef.protocol_objects.count()) + '"}', content_type="application/json");  


class BrowseProtocolsView(ListView):
    '''
    Extends ListView to return all protocols
    '''
    template_name = 'protocols/browse_protocols.html'
    
    queryset = SourceCitationRef.protocol_objects.order_by('source_citation')
    
    
class ProtocolSummaryView(DetailView):
    '''
    Extends DetailView to return a specific protocol
    '''
    template_name = 'protocols/protocol_summary.html'
    
    queryset = SourceCitationRef.protocol_objects.all()
    
    context_object_name = 'protocol'
        