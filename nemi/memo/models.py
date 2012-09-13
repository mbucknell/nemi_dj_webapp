from django.db import models

class DistinctManager(models.Manager):
	'''
	Extend the default manager to always perform a SELECT DISTINCT query.
	'''
	def get_query_set(self):
		return super(DistinctManager, self).get_query_set().distinct()

class AnalyteListACT(models.Model):
	analyte_name = models.CharField(max_length=240)
	analyte_id = models.IntegerField(primary_key=True)
	
	class Meta:
		db_table = u'ANALYTE_LIST_ACT'
		managed = False
		
	def __unicode__(self):
		return self.analyte_name
	
class SensorInfoVw(models.Model):	
	name = models.CharField(max_length=4000, blank=True)
	model_name = models.CharField(max_length=2000, blank=True)
	model_number = models.CharField(max_length=2000, blank=True)
	mfrcompany = models.CharField(max_length=2000, blank=True)
	analyte = models.CharField(max_length=4000, blank=True)
	accuracy = models.CharField(max_length=4000, blank=True)
	sample_rate = models.CharField(max_length=2000, blank=True)
	resolution = models.CharField(max_length=2000, blank=True)
	sensitivity = models.CharField(max_length=2000, blank=True)
	manufacturer = models.CharField(max_length=2000, blank=True)
	fm_pk_sensorid = models.IntegerField(primary_key=True)
	analyte_id = models.IntegerField()
	analyte_name = models.CharField(max_length=240)
	method_no = models.CharField(max_length=4000, blank=True)
	method_id = models.IntegerField(null=True)
	
	class Meta:
		db_table = u'SENSOR_INFO_VW'
		managed = False
		
	def __unicode__(self):
		return self.name
		
class MethodAnalyteACT(models.Model):
	method_descriptive_name = models.CharField(max_length=450, blank=True)
	method_official_name = models.CharField(max_length=250)
	brief_method_summary = models.CharField(max_length=4000)
	scope_and_application = models.CharField(max_length=2000, blank=True)
	analyte_name = models.CharField(max_length=240)
	accuracy = models.CharField(max_length=81, blank=True)
	precision = models.CharField(max_length=71, blank=True)
	DL = models.CharField(max_length=61, blank=True)
	false_positive_value = models.IntegerField(null=True)
	false_negative_value = models.IntegerField(null=True)
	method_number = models.CharField(max_length=30, blank=True)
	method_id = models.IntegerField(primary_key=True)
	resolution = models.CharField(max_length=2000, blank=True)
	sensitivity = models.CharField(max_length=2000, blank=True)
	sample_rate = models.CharField(max_length=2000, blank=True)
	mfrcompany = models.CharField(max_length=2000, blank=True)
	fm_pk_sensorid = models.IntegerField(null=True)
	
	class Meta:
		db_table = u'METHOD_ANALYTE_ACT'
		managed = False
		
	def __unicode__(self):
		return self.method_official_name
		
class MethodSensorAnalyteListACT(models.Model):
	analyte_name = models.CharField(max_length=240)
	analyte_id = models.IntegerField(primary_key=True)
	method_id = models.IntegerField(null=True)
	
	class Meta:
		db_table = u'METHOD_SENSOR_ANALYTE_LIST_ACT'
		managed = False
	
	def __unicode__(self):
		return self.analyte_name
		
	objects = DistinctManager()

class MethodSensorListACT(models.Model):
	method_no = models.CharField(max_length=2000, blank=True)
	method_id = models.IntegerField(primary_key=True)
	analyte_id = models.IntegerField(null=True)
	
	class Meta:
		db_table = u'METHOD_SENSOR_LIST_ACT'
		managed = False
		
	def __unicode__(self):
		return self.method_no
		
	objects = DistinctManager()
		
class MethodAnalyteVw(models.Model):
	DL_units = models.CharField(max_length=20)
	DL_value = models.IntegerField(null=True)
	sub_DL_value = models.CharField(max_length=40, blank=True)
	analyte_method_id = models.IntegerField(primary_key=True)
	analyte_id = models.IntegerField()
	accuracy = models.IntegerField(null=True)
	sub_accuracy = models.CharField(max_length=40, blank=True)
	accuracy_order = models.IntegerField(null=True)
	accuracy_units = models.CharField(max_length=40, blank=True)
	precision = models.IntegerField(null=True)
	sub_precision = models.CharField(max_length=40, blank=True)
	precision_units = models.CharField(max_length=30, blank=True)
	prec_acc_conc_used = models.IntegerField(null=True)
	false_positive_value = models.IntegerField(null=True)
	false_negative_value = models.IntegerField(null=True)
	analyte_code = models.CharField(max_length=20, blank=True)
	analyte_name = models.CharField(max_length=240, blank=True)
	preferred = models.IntegerField(null=True)
	analyte_cbr = models.CharField(max_length=1, blank=True)
	DL_units_description = models.CharField(max_length=60, blank=True)
	precision_units_description = models.CharField(max_length=100, blank=True)
	accuracy_units_description = models.CharField(max_length=50, blank=True)
	method_id = models.IntegerField()
	source_method_identifier = models.CharField(max_length=30)
	method_descriptive_name = models.CharField(max_length=450, blank=True)
	method_official_name = models.CharField(max_length=250)
	method_source_id = models.IntegerField(null=True)
	source_citation_id = models.IntegerField()
	brief_method_summary = models.CharField(max_length=4000)
	scope_and_application = models.CharField(max_length=2000, blank=True)
	media_name = models.CharField(max_length=30, blank=True)
	DL_type_id = models.IntegerField(null=True)
	DL_note = models.CharField(max_length=2000, blank=True)
	applicable_conc_range = models.CharField(max_length=300, blank=True)
	conc_range_units = models.CharField(max_length=20, blank=True)
	interferences = models.CharField(max_length=3000, blank=True)
	cbr_only = models.CharField(max_length=1, blank=True)
	qc_requirements = models.CharField(max_length=2000, blank=True)
	instrumentation_id = models.IntegerField(null=True)
	instrumentation = models.CharField(max_length=20)
	instrumentation_description = models.CharField(max_length=200)
	precision_descriptor_notes = models.CharField(max_length=3000, blank=True)
	link_to_full_method = models.CharField(max_length=240, blank=True)
	sample_handling = models.CharField(max_length=3000, blank=True)
	max_holding_time = models.CharField(max_length=300, blank=True)
	sample_prep_methods = models.CharField(max_length=100, blank=True)
	relative_cost_id = models.IntegerField(null=True)
	method_source = models.CharField(max_length=20, blank=True)
	method_source_name = models.CharField(max_length=150, blank=True)
	method_source_url = models.CharField(max_length=200, blank=True)
	method_subcategory_id = models.IntegerField()
	method_category = models.CharField(max_length=50)
	method_subcategory = models.CharField(max_length=40)
	DL_type = models.CharField(max_length=11, blank=True)
	DL_type_description = models.CharField(max_length=50, blank=True)
	source_citation_name = models.CharField(max_length=450, blank=True)
	source_citation = models.CharField(max_length=30)
	source_citation_information = models.CharField(max_length=1500, blank=True)
	relative_cost_symbol = models.CharField(max_length=7, blank=True)
	relative_cost = models.CharField(max_length=40, blank=True)
	matrix = models.CharField(max_length=12, blank=True)
	
	class Meta:
		db_table = u'METHOD_ANALYTE_VW'
		managed = False
		
	def __unicode__(self):
		return self.method_official_name
		
class SensorsACT(models.Model):
	fm_pk_sensorid = models.IntegerField(primary_key=True)
	model_name = models.CharField(max_length=2000, blank=True)
	mfrcompany = models.CharField(max_length=2000, blank=True)
	sensorimage = models.CharField(max_length=2000, blank=True)
	accuracy = models.CharField(max_length=2000, blank=True)
	resolution = models.CharField(max_length=2000, blank=True)
	sensitivity = models.CharField(max_length=2000, blank=True)
	sample_rate = models.CharField(max_length=2000, blank=True)
	range = models.CharField(max_length=2000, blank=True)
	weight = models.CharField(max_length=2000, blank=True)
	power_supply = models.CharField(max_length=2000, blank=True)
	battery_life = models.CharField(max_length=2000, blank=True)
	output = models.CharField(max_length=2000, blank=True)
	operating_temp = models.CharField(max_length=2000, blank=True)
	depth_capability = models.CharField(max_length=2000, blank=True)
	dimensions = models.CharField(max_length=2000, blank=True)
	cost = models.CharField(max_length=2000, blank=True)
	web_page = models.CharField(max_length=2000, blank=True)
	model_description = models.CharField(max_length=2000, blank=True)
	mfrstreet = models.CharField(max_length=2000, blank=True)
	mfrcity = models.CharField(max_length=2000, blank=True)
	mfrstateprovince = models.CharField(max_length=2000, blank=True)
	mfrpostalcode = models.CharField(max_length=2000, blank=True)
	mfrcountry = models.CharField(max_length=2000, blank=True)
	mfrtelephone = models.CharField(max_length=2000, blank=True)
	mfrfax = models.CharField(max_length=2000, blank=True)
	mfrwebsite = models.CharField(max_length=2000, blank=True)
	
	class Meta:
		db_table = u'SENSORS_ACT'
		managed = False
		
	def __unicode__(self):
		return self.model_name
		
	objects = DistinctManager()
		
class AnalyteInfo(models.Model):
	analyte_id = models.IntegerField(primary_key=True)
	description = models.CharField(max_length=4000)
	
	class Meta:
		db_table = u'ANALYTE_INFO'
		managed = False
		
	def __unicode__(self):
		return self.description