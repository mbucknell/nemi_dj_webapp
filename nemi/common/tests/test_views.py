
import StringIO

from django.http import Http404
from django.test import TestCase

from ..views import ChoiceJsonView, PdfView

class CommonJsonViewTestCase(TestCase):

    def test_response(self):
        class TestView(ChoiceJsonView):
            def get_choices(self, request, *args, **kwargs):
                return [('value1', 'Value 1'), ('value2', 'Value 2'), ('value3', 'Value 3')]
    
        test_view = TestView()
        request = ''
        resp = test_view.get(request)
        
        self.assertEqual(resp.content, '{"choices" : [{"value" : "value1", "display_value" : "Value 1"},{"value" : "value2", "display_value" : "Value 2"},{"value" : "value3", "display_value" : "Value 3"}]}')
        
    def test_no_data_response(self):
        class TestView(ChoiceJsonView):
            def get_choices(self, request, *args, **kwargs):
                return []
            
        test_view = TestView()
        request = ''
        resp = test_view.get(request)
        
        self.assertEqual(resp.content, '{"choices" : []}')
        
        
class PdfViewTestCase(TestCase):
    def test_response_no_data(self):
        test_view = PdfView()
        request = ''
        
        self.assertEquals(test_view.get(request), Http404)
        
    def test_response_with_data(self):   
        class TestPdfView(PdfView):
            mimetype = 'application/pdf'
            pdf = StringIO.StringIO('Test PDF String')
            filename = 'test'
            
        test_view = TestPdfView()
        request = ''
        
        resp = test_view.get(request)
        self.assertEquals(resp['Content-Type'], 'application/pdf')
        self.assertEquals(resp['content-disposition'],'attachment;filename=test.pdf')
        self.assertContains(resp,'Test PDF String')
            
    