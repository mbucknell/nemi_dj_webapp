
import mock
import StringIO

from django.http import Http404
from django.test import TestCase
from django.test.client import RequestFactory

from ..views import ChoiceJsonView, PdfView, SimpleWebProxyView

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
            
class SimpleWebProxyViewTestCase(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.test_view = SimpleWebProxyView(service_url='http://www.fake.com/service')
        
    def test_successful_get(self):
        with mock.patch('common.views.requests.get') as mock_requests_get:
            resp = mock.Mock
            resp.text = 'It was successful'
            resp.status_code = 200
            resp.headers = {'content-type' : 'text/xml', 'content-disposition' : 'attachment;filename="Results.xml"'}
            
            args = []
            kwargs = {'op' : 'specific_op/'}
            request = self.factory.get('/my_service/specific_op/?param1=1&param2=2')
            
            response = self.test_view.get(request, *args, **kwargs)
            
            self.assertEqual(mock_requests_get.call_args[0], ('http://www.fake.com/service/specific_op/?param1=1&param2=2',))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, 'It was successful')
            self.assertEqual(response['Content-Type'], 'text/xml')
            self.assertEqual(response['Content-Disposition'], 'attachment;filename="Results.xml"')
            
    def test_unsuccssful_get(self):
        with mock.patch('common.views.requests.get') as mock_requests_get:
            resp = mock.Mock
            resp.text = 'Failure'
            resp.status_code = 404
            
            args = []
            kwargs = {'op' : 'specific_op/'}
            request = self.factory.get('/my_service/specific_op/?param1=1&param2=2')
            
            response = self.test_view.get(request, *args, **kwargs)
            
            self.assertEqual(mock_requests_get.call_args[0], ('http://www.fake.com/service/specific_op/?param1=1&param2=2',))
            self.assertEqual(response.status_code, 404)

    def test_successful_head(self):
        with mock.patch('common.views.requests.head') as mock_requests_head:
            resp = mock.Mock
            resp.text = 'It was successful'
            resp.status_code = 200
            resp.headers = {'content-type' : 'text/xml', 
                            'content-disposition' : 'attachment;filename="Results.xml"',
                            'custom-header' : 'Custom header value'}
            
            args = []
            kwargs = {'op' : 'specific_op/'}
            request = self.factory.head('/my_service/specific_op/?param1=1&param2=2')
            
            response = self.test_view.head(request, *args, **kwargs)
            
            self.assertEqual(mock_requests_head.call_args[0], ('http://www.fake.com/service/specific_op/?param1=1&param2=2',))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, 'It was successful')
            self.assertEqual(response['Content-Type'], 'text/xml')
            self.assertEqual(response['Content-Disposition'], 'attachment;filename="Results.xml"')
            self.assertEqual(response['custom-header'], 'Custom header value')
            
    def test_unsuccssful_head(self):
        with mock.patch('common.views.requests.head') as mock_requests_head:
            resp = mock.Mock
            resp.text = 'Failure'
            resp.status_code = 404
            
            args = []
            kwargs = {'op' : 'specific_op/'}
            request = self.factory.head('/my_service/specific_op/?param1=1&param2=2')
            
            response = self.test_view.head(request, *args, **kwargs)
            
            self.assertEqual(mock_requests_head.call_args[0], ('http://www.fake.com/service/specific_op/?param1=1&param2=2',))
            self.assertEqual(response.status_code, 404)

    def test_invalid_method(self):
        args = []
        kwargs = {'op' : 'specific_op/'}
        request = self.factory.post('/my_service/specific_op/?param1=1&param2=2')
        
        response = SimpleWebProxyView.as_view()(request, *args, **kwargs)
        
        self.assertEqual(response.status_code, 405)