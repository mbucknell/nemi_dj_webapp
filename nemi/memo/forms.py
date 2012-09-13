from django.forms import Form, ChoiceField, ModelChoiceField, MultipleChoiceField
from django.forms.widgets import Select, SelectMultiple

from models import AnalyteListACT, MethodSensorAnalyteListACT, MethodSensorListACT, SensorInfoVw

class MemoAnalyteSearchForm(Form):
	'''Extends the standard form to implement the query-filtering form for MEMO Analyte Search'''
	analyte = ModelChoiceField(queryset=AnalyteListACT.objects,
							   label='Analyte',
							   empty_label='Any',
							   required=False,
							   help_text='Select sensors for a given analyte')
							
class MemoCombinedSearchForm(Form):
	'''
	Extends the standard form to implement the query-filtering form for MEMO Combined Search.
	Choice fields are retrieved from the database on page view.
	'''
	analyte = ChoiceField(choices=[('', 'Any')] + [(row['analyte_id'], row['analyte_name']) for row in MethodSensorAnalyteListACT.objects.order_by('analyte_name').values('analyte_name', 'analyte_id').distinct()],
						  label='Analyte',
						  required=False,
						  help_text='Select sensors for a given analyte',
						  widget=Select(attrs={'id':'analyte-select', 'style':'width: 20em'}))
							
	method = ChoiceField(choices=[('', 'Any')] + [(row['method_id'], row['method_no']) for row in MethodSensorListACT.objects.order_by('method_no').values('method_no', 'method_id').distinct()],
							  label='Method',
							  required=False,
							  help_text='Select sensors for a given method',
							  widget=Select(attrs={'id':'method-select', 'style':'width: 7em'}))
												
class MemoSensorSearchForm(Form):
	'''
	Extends the standard form to implement the query-filtering form for MEMO Sensor Search.
	'''
	analyte = ChoiceField(choices=[('', 'Any')] + [(row['analyte_id'], row['analyte_name']) for row in SensorInfoVw.objects.order_by('analyte_name').values('analyte_name', 'analyte_id').distinct()],
							   label='Analyte',
							   required=False,
							   help_text='Select sensors for a given analyte',
							   widget=Select(attrs={'id':'analyte-select', 'style':'width: 20em'}))
	
	mfr = MultipleChoiceField(choices=[('', 'Any')] + [(row['manufacturer'], row['manufacturer']) for row in SensorInfoVw.objects.order_by('manufacturer').values('manufacturer').distinct()],
							label='Manufacturer',
							required=False,
							help_text='Select sensors from a given manufacturer',
							widget=SelectMultiple(attrs={'id':'mfr-select', 'style':'width: 20em'}))