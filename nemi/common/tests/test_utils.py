'''
Created on Mar 15, 2012

@author: mbucknel
'''

from django import forms 
from django.test import SimpleTestCase, TestCase

from nemi_project.test_settings_mgr import TestSettingsManager

from ..utils.forms import get_criteria, get_criteria_from_field_data, get_multi_choice
from ..utils.view_utils import tsv_response, xls_response
from models import TestModel


class GetCriteriaTestCase(SimpleTestCase):
    
    def test_choice_select_integer_value(self):
        class MyForm(forms.Form):
            choice_field = forms.ChoiceField(choices=[('all', 'Any'), (1, 'One'), (2, 'Two'), (3, 'Three')])       
                
        test_form = MyForm(data={'choice_field' : 1})
        self.assertEqual(get_criteria(test_form['choice_field']), ('Choice field', 'One'))
        
        test_form = MyForm(data={'choice_field' : 'all'})
        self.assertIsNone(get_criteria(test_form['choice_field']))
        
    def test_choice_select_string_value(self):
        class MyForm(forms.Form):
            choice_field = forms.ChoiceField(choices=[('all', 'Any'), ('one', 'One'), ('two', 'Two'), ('three', 'Three')]) 
            
        test_form = MyForm(data={'choice_field' : 'two'})
        self.assertEqual(get_criteria(test_form['choice_field']), ('Choice field', 'Two')) 
        
        test_form = MyForm(data={'choice_field' : 'all'})
        self.assertIsNone(get_criteria(test_form['choice_field']))
        
    def test_not_choice_field(self):
        class MyForm(forms.Form):
            char_field = forms.CharField(max_length=10)
            
        test_form = MyForm(data={'char_field' : 'one'})
        self.assertRaises(AttributeError, get_criteria, (test_form['char_field']))   
                
        
class GetCriteriaFromFieldDataTestCase(TestCase):
    
    class MyForm(forms.Form):
        choice = forms.ModelChoiceField(queryset=TestModel.objects.all(), required=False)
        char = forms.CharField(max_length=10, required=False)
        my_int = forms.IntegerField(required=False)
        
    def __init__(self, *args, **kwargs):
        super(GetCriteriaFromFieldDataTestCase, self).__init__(*args, **kwargs)
        self.settings_manager = TestSettingsManager()    

    def setUp(self):
        self.settings_manager.set(INSTALLED_APPS=('common','common.tests'))
            
        self.m1 = TestModel.objects.create(name='Item 1')        
        self.m2 = TestModel.objects.create(name='Item 2')
        self.m3 = TestModel.objects.create(name='Item 3')
        
    def test_with_no_selection(self):
        my_form = self.MyForm(data={'choice' : None,
                                    'char' : '',
                                    'my_int' : ''})
        
        my_form.is_valid()
        self.assertIsNone(get_criteria_from_field_data(my_form, 'choice'))
        self.assertEqual(get_criteria_from_field_data(my_form, 'char'), ('Char', ''))
        self.assertIsNone(get_criteria_from_field_data(my_form, 'my_int'))
        
    def test_with_selection(self):
        my_form = self.MyForm({'choice' : self.m2.pk,
                               'char' : 'name',
                               'my_int' : 12})
        my_form.is_valid()
        result_choice = get_criteria_from_field_data(my_form, 'choice')
        self.assertEqual(result_choice[0], 'Choice')
        self.assertEqual(result_choice[1], self.m2)
        self.assertEqual(get_criteria_from_field_data(my_form, 'char'), ('Char', 'name'))
        self.assertEqual(get_criteria_from_field_data(my_form, 'my_int'), ('My int', 12))
        
    def test_with_label_overrider(self):
        my_form = self.MyForm({'choice' : self.m2.pk,
                               'char' : 'name',
                               'my_int' : 12})
        my_form.is_valid()
        result_choice = get_criteria_from_field_data(my_form, 'choice', 'What is my choice')
        self.assertEqual(result_choice[0], 'What is my choice')
        self.assertEqual(result_choice[1], self.m2)
        
                
    def test_with_bad_field(self):
        my_form = self.MyForm(data={'choice' : None,
                                    'char' : '',
                                    'my_int' : ''})

        self.assertRaises(AttributeError, get_criteria_from_field_data, my_form, 'choice')
        
        my_form.is_valid()
        self.assertRaises(KeyError, get_criteria_from_field_data, my_form, 'bad_choice')
        
    def tearDown(self):
        self.settings_manager.revert()
        
class GetMultiChoiceTestCase(SimpleTestCase):
    
    def test_with_string_values(self):
        class MyForm(forms.Form):
            multi_choice = forms.MultipleChoiceField(choices=[('c1', 'Choice 1'), ('c2', 'Choice 2'), ('c3', 'Choice 3')])
            
        my_form = MyForm(data={'multi_choice' : ['c1', 'c3']})
        my_form.is_valid()
        self.assertEqual(get_multi_choice(my_form, 'multi_choice'), ['Choice 1', 'Choice 3'])
        
        my_form = MyForm(data={'multi_choice' : ['c2']})
        my_form.is_valid()
        self.assertEqual(get_multi_choice(my_form, 'multi_choice'), ['Choice 2'])
        
    def test_with_integer_values(self):
        class MyForm(forms.Form):
            multi_choice = forms.MultipleChoiceField(choices=[(1, 'Choice 1'), (2, 'Choice 2'), (3, 'Choice 3')])
            
        my_form = MyForm(data={'multi_choice' : [2, 3]})
        my_form.is_valid()
        self.assertEqual(get_multi_choice(my_form, 'multi_choice'), ['Choice 2', 'Choice 3'])
        
        my_form = MyForm(data={'multi_choice' : [1]})
        my_form.is_valid()
        self.assertEqual(get_multi_choice(my_form, 'multi_choice'), ['Choice 1'])

    def test_bad_field(self):
        class MyForm(forms.Form):
            multi_choice = forms.MultipleChoiceField(choices=[(1, 'Choice 1'), (2, 'Choice 2'), (3, 'Choice 3')])
            
        my_form = MyForm(data={'multi_choice' : [1, 2]})
        my_form.is_valid()
        self.assertRaises(KeyError, get_multi_choice, my_form, 'another_field')
            
class TsvResponseTestCase(SimpleTestCase):
    
    def test_response(self):
        headings = ['A', 'B', 'C']
        list_of_lists = [['A1,', 'B1', 10], ['A2', 'B2', 20], ['A3', 'B3', 30]]
        filename = 'test'
        response = tsv_response(headings, list_of_lists, filename)
        
        self.assertEqual(response['Content-Type'],'text/tab-separated-values')  
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=%s.tsv' % filename) 
        
        expected_contents = '\t'.join(headings) + '\n'
        for row in list_of_lists:
            for col in row:
                expected_contents += '%s\t' % str(col)
            expected_contents += '\n'
        self.assertEqual(response.content, expected_contents)
        self.assertEqual(response.status_code, 200) 
        
class XlsResponseTestCase(SimpleTestCase):
    
    def test_response(self):
        headings = ['A', 'B', 'C']
        list_of_lists = [['A1,', 'B1', 10], ['A2', 'B2', 20], ['A3', 'B3', 30]]
        filename = 'test'
        response = xls_response(headings, list_of_lists, filename)
        
        self.assertEqual(response['Content-Type'],'application/vnd.ms-excel')  
        self.assertEqual(response['Content-Disposition'], 'attachment; filename=%s.xls' % filename)         
