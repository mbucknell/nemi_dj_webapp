
from django.utils import unittest

from common.views import ChoiceJsonView

class TestCommonJsonView(unittest.TestCase):

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