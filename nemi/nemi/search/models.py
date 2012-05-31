''' This module contain the model class defintions for the tables and views
that are used to implement the NEMI search pages. All tables and views are read
only and therefore have managed set to Fasle in each model's Meta data.
'''

from django.contrib.auth.models import User
from django.db import models

class MethodVW(models.Model):
    
    method_id = models.IntegerField(primary_key=True)
    source_method_identifier = models.CharField(max_length=30)
    method_descriptive_name = models.CharField(max_length=250)
    method_official_name = models.CharField(max_length=250)
    method_source_id = models.IntegerField()
    source_citation_id = models.IntegerField()
    brief_method_summary = models.CharField(max_length=4000)
    scope_and_application = models.CharField(max_length=2000, blank=True)
    media_name = models.CharField(max_length=30)
    dl_type_id = models.IntegerField(null=True)
    dl_note = models.CharField(max_length=2000, blank=True)
    applicable_conc_range = models.CharField(max_length=300, blank=True)
    conc_range_units = models.CharField(max_length=20, blank=True)
    interferences = models.CharField(max_length=3000, blank=True)
    qc_requirements = models.CharField(max_length=2000, blank=True)
    cbr_only = models.CharField(max_length=1, blank=True)
    link_to_full_method = models.CharField(max_length=240, blank=True)
    sample_handling = models.CharField(max_length=3000, blank=True)
    max_holding_time = models.CharField(max_length=300, blank=True)
    sample_prep_methods = models.CharField(max_length=100, blank=True)
    relative_cost_id = models.IntegerField(null=True)
    instrumentation_id = models.IntegerField()
    precision_descriptor_notes = models.CharField(max_length=3000, blank=True)
    screening = models.CharField(max_length=8, blank=True)
    rapidity = models.CharField(max_length=30, blank=True)
    waterbody_type = models.CharField(max_length=20, blank=True)
    matrix = models.CharField(max_length=12, blank=True)
    method_source = models.CharField(max_length=20)
    method_source_name = models.CharField(max_length=150)
    method_source_contact = models.CharField(max_length=450, blank=True)
    method_source_url = models.CharField(max_length=200, blank=True)
    method_subcategory_id = models.IntegerField()
    method_category = models.CharField(max_length=50)
    method_subcategory = models.CharField(max_length=40)
    dl_type = models.CharField(max_length=11, blank=True)
    dl_type_description = models.CharField(max_length=50, blank=True)
    source_citation_name = models.CharField(max_length=450, blank=True)
    source_citation = models.CharField(max_length=30)
    source_citation_information = models.CharField(max_length=1500, blank=True)
    relative_cost_symbol = models.CharField(max_length=7, blank=True)
    relative_cost = models.CharField(max_length=40, blank=True)
    cost_effort_key = models.CharField(max_length=10, blank=True)
    instrumentation = models.CharField(max_length=20)
    instrumentation_description = models.CharField(max_length=200)
    regs_only = models.CharField(max_length=1)
    method_type_desc = models.CharField(max_length=100, blank=True)
    method_type_id = models.IntegerField()
    date_loaded = models.DateField(null=True)
    collected_sample_amt_ml = models.CharField(max_length=10, blank=True)
    collected_sample_amt_g = models.CharField(max_length=10, blank=True)
    liquid_sample_flag = models.CharField(max_length=1, blank=True)
    analysis_amt_ml = models.CharField(max_length=10, blank=True)
    analysis_amt_g = models.CharField(max_length=10, blank=True)
    ph_of_analytical_sample = models.CharField(max_length=10, blank=True)
    calc_waste_amt = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    quality_review_id = models.CharField(max_length=100, blank=True)
    pbt = models.CharField(max_length=1, blank=True)
    toxic = models.CharField(max_length=1, blank=True)
    corrosive = models.CharField(max_length=1, blank=True)
    waste = models.CharField(max_length=1, blank=True)
    assumptions_comments = models.CharField(max_length=2000, blank=True)
    
    class Meta:
        db_table = u'method_vw'
        managed = False
                
class MethodSummaryVW(models.Model):
    
    revision_id = models.IntegerField()
    revision_information = models.CharField(max_length=100)
    revision_flag = models.IntegerField(null=True)
    mimetype = models.CharField(max_length=50, blank=True)
#    mydoc -- Unused
#    method_pdf -- Unused
    pdf_size  = models.IntegerField(blank=True)
    method_id = models.IntegerField(primary_key=True) 
    source_method_identifier = models.CharField(max_length=30)
    method_descriptive_name = models.CharField(max_length=250)
    method_official_name = models.CharField(max_length=250)
    method_source_id = models.IntegerField()
    source_citation_id = models.IntegerField()
    brief_method_summary = models.CharField(max_length=4000)
    scope_and_application = models.CharField(max_length=2000, blank=True)
    media_name = models.CharField(max_length=30)
    dl_type_id = models.IntegerField(null=True)
    dl_note = models.CharField(max_length=2000, blank=True)
    applicable_conc_range = models.CharField(max_length=300, blank=True)
    conc_range_units = models.CharField(max_length=20, blank=True)
    interferences = models.CharField(max_length=3000, blank=True)
    method_source_contact = models.CharField(max_length=450, blank=True)
    qc_requirements = models.CharField(max_length=2000, blank=True)
    waterbody_type = models.CharField(max_length=20, blank=True)
    link_to_full_method = models.CharField(max_length=240, blank=True)
    sample_handling = models.CharField(max_length=3000, blank=True)
    max_holding_time = models.CharField(max_length=300, blank=True)
    sample_prep_methods = models.CharField(max_length=100, blank=True)
    relative_cost_id = models.IntegerField(blank=True)
    method_source = models.CharField(max_length=20)
    method_source_name = models.CharField(max_length=150)
    method_source_url = models.CharField(max_length=200, blank=True)
    precision_descriptor_notes = models.CharField(max_length=3000, blank=True)
    method_subcategory_id = models.IntegerField()
    method_category = models.CharField(max_length=50)
    method_subcategory = models.CharField(max_length=40)
    method_type_desc = models.CharField(max_length=100, blank=True)
    dl_type = models.CharField(max_length=11, blank=True)
    dl_type_description = models.CharField(max_length=50, blank=True)
    source_citation_name = models.CharField(max_length=450, blank=True)
    source_citation = models.CharField(max_length=30)
    source_citation_information = models.CharField(max_length=1500, blank=True)
    relative_cost_symbol = models.CharField(max_length=7, blank=True)
    relative_cost = models.CharField(max_length=40, blank=True)
    pdf_name = models.CharField(max_length=34, blank=True)
    pdf_name2 = models.CharField(max_length=44, blank=True)
    collected_sample_amt_ml = models.CharField(max_length=10, blank=True)
    collected_sample_amt_g = models.CharField(max_length=10, blank=True)
    liquid_sample_flag = models.CharField(max_length=1, blank=True)
    analysis_amt_ml = models.CharField(max_length=10, blank=True)
    analysis_amt_g = models.CharField(max_length=10, blank=True)
    ph_of_analytical_sample = models.CharField(max_length=10, blank=True)
    calc_waste_amt = models.DecimalField(max_digits=9, decimal_places=2, blank=True)
    quality_review_id = models.CharField(max_length=100, blank=True)
    pbt = models.CharField(max_length=1, blank=True)
    toxic = models.CharField(max_length=1, blank=True)
    corrosive = models.CharField(max_length=1, blank=True)
    waste = models.CharField(max_length=1, blank=True)
    assumptions_comments = models.CharField(max_length=2000, blank=True)
     
    class Meta:
        db_table = u'method_summary_vw'
        managed = False
        
class MethodAnalyteVW(models.Model):
     
    sample_handling = models.CharField(max_length=3000, blank=True)
    max_holding_time = models.CharField(max_length=300, blank=True)
    sample_prep_methods = models.CharField(max_length=100, blank=True)
    relative_cost_id = models.IntegerField(null=True)
    method_source = models.CharField(max_length=20)
    method_source_name = models.CharField(max_length=150)
    method_source_url = models.CharField(max_length=200, blank=True)
    method_subcateory_id = models.IntegerField()
    method_category = models.CharField(max_length=50)
    method_subcategory = models.CharField(max_length=40)
    dl_type = models.CharField(max_length=11)
    dl_type_description = models.CharField(max_length=50)
    source_citation_name = models.CharField(max_length=450, blank=True)
    source_citation = models.CharField(max_length=30)
    source_citation_information = models.CharField(max_length=1500, blank=True)
    relative_cost_symbol = models.CharField(max_length=7, blank=True)
    relative_cost = models.CharField(max_length=40, blank=True)
    matrix = models.CharField(max_length=12, blank=True)
    dl_units = models.CharField(max_length=20)
    dl_value = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    sub_dl_value = models.CharField(max_length=40, blank=True)
    analyte_method_id = models.IntegerField(primary_key=True)
    analyte_id = models.IntegerField()
    accuracy = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    sub_accuracy = models.CharField(max_length=40, blank=True)
    accuracy_order = models.IntegerField(null=True)
    accuracy_units = models.CharField(max_length=40, blank=True)
    precision = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    sub_precision = models.CharField(max_length=40, blank=True)
    precision_units= models.CharField(max_length=30, blank=True)
    prec_acc_conc_used = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    false_positive_value = models.IntegerField(null=True)
    false_negative_value = models.IntegerField(null=True)
    analyte_code = models.CharField(max_length=20, blank=True)
    analyte_name = models.CharField(max_length=240, blank=True)
    preferred = models.IntegerField(null=True)
    analyte_cbr = models.CharField(max_length=1, blank=True)
    dl_units_description = models.CharField(max_length=60, blank=True)
    precision_units_description = models.CharField(max_length=100, blank=True)
    accuracy_units_description = models.CharField(max_length=50, blank=True)
    method_id = models.IntegerField(null=True)
    source_method_identifier = models.CharField(max_length=30)
    method_descriptive_name = models.CharField(max_length=250)
    method_official_name = models.CharField(max_length=250)
    method_source_id = models.IntegerField()
    source_citation_id = models.IntegerField()
    brief_method_summary = models.CharField(max_length=4000)
    scope_and_application = models.CharField(max_length=2000, blank=True)
    media_name = models.CharField(max_length=30)
    dl_type_id = models.IntegerField(null=True)
    dl_note = models.CharField(max_length=2000, blank=True)
    applicable_conc_range = models.CharField(max_length=300, blank=True)
    conc_range_units = models.CharField(max_length=20, blank=True)
    interferences = models.CharField(max_length=3000, blank=True)
    cbr_only = models.CharField(max_length=1, blank=True)
    qc_requirements = models.CharField(max_length=2000, blank=True)
    instrumentation_id = models.IntegerField()
    instrumentation = models.CharField(max_length=20)
    instrumentation_description = models.CharField(max_length=200)
    precision_descriptor_notes = models.CharField(max_length=3000, blank=True)
    link_to_full_method = models.CharField(max_length=240, blank=True)
    
    class Meta:
        db_table = u'method_analyte_vw'
        managed = False
        
class DefinitionsDOM(models.Model):
    
    definition_name = models.CharField(max_length=75, primary_key=True)
    definition_description = models.CharField(max_length=1500)
    definition_abbrev = models.CharField(max_length=30)
    web_desc_bio = models.CharField(max_length=4000, blank=True)
    web_desc_all = models.CharField(max_length=4000, blank=True)
    web_desc_phys = models.CharField(max_length=4000, blank=True)
    column_help = models.CharField(max_length=4000, blank=True)
    
    class Meta:
        db_table = u'definitions_dom'
        managed = False

class AnalyteCodeRel(models.Model):
    
    analyte_code = models.CharField(max_length=20)
    analyte_name = models.CharField(max_length=240, primary_key=True)
    preferred = models.IntegerField(null=True)
    changed = models.DateField()
    data_entry = models.CharField(max_length=20, blank=True)
    analyte_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = u'analyte_code_rel'
        managed = False

class MethodAnalyteAllVW(models.Model):
    
    analysis_amt_g = models.CharField(max_length=10, blank=True)
    ph_of_analytical_sample = models.CharField(max_length=10, blank=True)
    calc_waste_amt = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    quality_review_id = models.CharField(max_length=100, blank=True)
    pbt = models.CharField(max_length=1, blank=True)
    toxic = models.CharField(max_length=1, blank=True)
    corrosive = models.CharField(max_length=1, blank=True)
    waste = models.CharField(max_length=1, blank=True)
    assumptions_comments = models.CharField(max_length=2000, blank=True)
    method_type_desc = models.CharField(max_length=100, blank=True)
    prec_acc_conc_used = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    false_positive_value = models.IntegerField(null=True)
    false_negative_value = models.IntegerField(null=True)
    dl_units_description = models.CharField(max_length=60, blank=True)
    precision_units_description = models.CharField(max_length=100, blank=True)
    accuracy_units_description = models.CharField(max_length=50, blank=True)
    instrumentation = models.CharField(max_length=20)
    instrumentation_description = models.CharField(max_length=200)
    analyte_code = models.CharField(max_length=20)
    analyte_name = models.CharField(max_length=240)
    preferred = models.IntegerField(null=True)
    usgs_pcode = models.CharField(max_length=6, blank=True)
    analyte_cbr = models.CharField(max_length=1, blank=True)
    analyte_type = models.CharField(max_length=50, blank=True)
    method_id = models.IntegerField()
    source_method_identifier = models.CharField(max_length=30)
    method_descriptive_name = models.CharField(max_length=250)
    method_official_name = models.CharField(max_length=250)
    method_source_id = models.IntegerField()
    source_citation_id = models.IntegerField()
    brief_method_summary = models.CharField(max_length=4000)
    scope_and_application = models.CharField(max_length=2000, blank=True)
    media_name = models.CharField(max_length=30)
    dl_type_id = models.IntegerField(null=True)
    dl_note = models.CharField(max_length=2000, blank=True)
    applicable_conc_range = models.CharField(max_length=300, blank=True)
    conc_range_units = models.CharField(max_length=20, blank=True)
    interferences = models.CharField(max_length=3000, blank=True)
    cbr_only = models.CharField(max_length=1, blank=True)
    qc_requirements = models.CharField(max_length=2000, blank=True)
    instrumentation_id = models.IntegerField(null=True)
    link_to_full_method = models.CharField(max_length=240, blank=True)
    sample_handling = models.CharField(max_length=3000, blank=True)
    max_holding_time = models.CharField(max_length=300, blank=True)
    waterbody_type = models.CharField(max_length=20, blank=True)
    sample_prep_methods = models.CharField(max_length=100, blank=True)
    relative_cost_id = models.IntegerField(null=True)
    method_source = models.CharField(max_length=20)
    method_source_name = models.CharField(max_length=150)
    method_source_url = models.CharField(max_length=200, blank=True)
    method_source_contact = models.CharField(max_length=450, blank=True)
    precision_descriptor_notes = models.CharField(max_length=3000, blank=True)
    method_subcategory_id = models.IntegerField()
    method_category = models.CharField(max_length=50)
    method_subcategory = models.CharField(max_length=40)
    dl_type = models.CharField(max_length=11, blank=True)
    dl_type_description = models.CharField(max_length=50, blank=True)
    source_citation_name = models.CharField(max_length=450, blank=True)
    source_citation = models.CharField(max_length=30)
    source_citation_information = models.CharField(max_length=1500, blank=True)
    relative_cost_symbol = models.CharField(max_length=7, blank=True)
    relative_cost = models.CharField(max_length=40, blank=True)
    cost_effort_key = models.CharField(max_length=10, blank=True)
    matrix = models.CharField(max_length=12, blank=True)
    collected_sample_amt_ml = models.CharField(max_length=10, blank=True)
    collected_sample_amt_g = models.CharField(max_length=10, blank=True)
    liquid_sample_flag = models.CharField(max_length=1, blank=True)
    analysis_amt_ml = models.CharField(max_length=10, blank=True)
    dl_units = models.CharField(max_length=20)
    dl_value = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    sub_dl_value = models.CharField(max_length=40, blank=True)
    analyte_method_id = models.IntegerField(primary_key=True)
    analyte_id = models.IntegerField()
    accuracy = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    sub_accuracy = models.CharField(max_length=40, blank=True)
    accuracy_order = models.IntegerField(null=True)
    accuracy_units = models.CharField(max_length=40, blank=True)
    precision = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    sub_precision = models.CharField(max_length=40, blank=True)
    precision_units = models.CharField(max_length=30, blank=True)
    
    class Meta:
        db_table = 'method_analyte_all_vw'
        managed = False
        
class AnalyteCodeVW(models.Model):
    
    analyte_analyte_id = models.IntegerField(primary_key=True)
    analyte_analyte_code = models.CharField(max_length=20)
    ac_analyte_code = models.CharField(max_length=20, blank=True)
    ac_analyte_name = models.CharField(max_length=240, blank=True)
    ac_preferred = models.IntegerField(null=True)
    ac_analyte_type = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'analyte_code_vw'
        managed = False
        
class StatisticalMediaNameManager(models.Manager):
    '''Extends the Manager class to provide a query set that returns valid media for statistical methods.
    '''
    
    def get_query_set(self):
        return super(StatisticalMediaNameManager, self).get_query_set().exclude(
            media_name__iexact='Various').exclude(media_name__iexact='Water').exclude(media_name__iexact='Sediment')
        
class MediaNameDOM(models.Model):
    
    media_name = models.CharField(primary_key=True, max_length=30)
    media_id = models.IntegerField()
    
    objects = models.Manager()
    stat_media = StatisticalMediaNameManager()
    
    class Meta:
        db_table = 'media_name_dom'
        ordering = ['media_name']
        managed = False
        
    def __unicode__(self):
        return self.media_name.lower().title()
        
class MethodSourceRef(models.Model):
    
    method_source_id = models.IntegerField(primary_key=True)
    method_source = models.CharField(max_length=20)
    method_source_url = models.CharField(max_length=200, blank=True)
    method_source_name = models.CharField(max_length=150)
    method_source_contact = models.CharField(max_length=450, blank=True)
    method_source_email = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'method_source_ref'
        managed = False
        ordering= ['method_source']
        
    def __unicode__(self):
        return self.method_source
        
class InstrumentationRef(models.Model):
    
    instrumentation_id = models.IntegerField(primary_key=True)
    instrumentation = models.CharField(max_length=20)
    instrumentation_description = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'instrumentation_ref'
        managed = False
        
class MethodSubcategoryRef(models.Model):
    
    method_subcategory_id = models.IntegerField(primary_key=True)
    method_category = models.CharField(max_length=50)
    method_subcategory = models.CharField(max_length=40)
    
    class Meta:
        db_table = 'method_subcategory_ref'
        managed = False
        
class MethodAnalyteJnStgVW(models.Model):
    
    matrix = models.CharField(max_length=12, blank=True)
    method_source = models.CharField(max_length=20)
    method_source_name = models.CharField(max_length=150)
    method_source_contact = models.CharField(max_length=450, blank=True)
    waterbody_type = models.CharField(max_length=20, blank=True)
    method_source_url = models.CharField(max_length=200, blank=True)
    technique = models.CharField(max_length=50, blank=True)
    method_subcategory_id = models.IntegerField()
    method_category = models.CharField(max_length=50)
    dl_type = models.CharField(max_length=11, blank=True)
    dl_type_description = models.CharField(max_length=50, blank=True)
    source_citation_name = models.CharField(max_length=450, blank=True)
    source_citation = models.CharField(max_length=30)
    source_citation_information = models.CharField(max_length=1500, blank=True)
    relative_cost_symbol = models.CharField(max_length=7, blank=True)
    relative_cost = models.CharField(max_length=40, blank=True)
    cost_effort_key = models.CharField(max_length=10, blank=True)
    dl_units = models.CharField(max_length=20, blank=True)
    dl_value = models.DecimalField(max_digits=21, decimal_places=6, blank=True)
    analyte_method_id = models.IntegerField(null=True)
    precision = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    analyte_id = models.IntegerField(null=True)
    accuracy = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    accuracy_units = models.CharField(max_length=40, blank=True)
    approved = models.CharField(max_length=1)
    precision_units = models.CharField(max_length=30, blank=True)
    prec_acc_conc_used = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    false_positive_value = models.IntegerField(null=True)
    false_negative_value = models.IntegerField(null=True)
    analyte_code = models.CharField(max_length=20, blank=True)
    analyte_name = models.CharField(max_length=240, blank=True)
    preferred = models.IntegerField(null=True)
    analyte_type = models.CharField(max_length=50, blank=True)
    dl_units_description = models.CharField(max_length=60, blank=True)
    precision_units_description = models.CharField(max_length=100, blank=True)
    accuracy_units_description = models.CharField(max_length=50, blank=True)
    method_id = models.IntegerField(primary_key=True)
    source_method_identifier = models.CharField(max_length=30)
    method_descriptive_name = models.CharField(max_length=250)
    method_official_name = models.CharField(max_length=250)
    method_source_id = models.IntegerField()
    source_citation_id = models.IntegerField()
    brief_method_summary = models.CharField(max_length=4000)
    scope_and_application = models.CharField(max_length=2000, blank=True)
    media_name = models.CharField(max_length=30)
    dl_type_id = models.IntegerField(null=True)
    dl_note = models.CharField(max_length=2000, blank=True)
    applicable_conc_range = models.CharField(max_length=300, blank=True)
    conc_range_units = models.CharField(max_length=20, blank=True)
    interferences = models.CharField(max_length=3000, blank=True)
    rapidity = models.CharField(max_length=30, blank=True)
    qc_requirements = models.CharField(max_length=2000, blank=True)
    instrumentation_id = models.IntegerField()
    instrumentation = models.CharField(max_length=20)
    instrumentation_description = models.CharField(max_length=200)
    precision_descriptor_notes = models.CharField(max_length=3000, blank=True)
    link_to_full_method = models.CharField(max_length=240, blank=True)
    sample_handling = models.CharField(max_length=3000, blank=True)
    max_holding_time = models.CharField(max_length=300, blank=True)
    sample_prep_methods = models.CharField(max_length=100, blank=True)
    relative_cost_id = models.IntegerField(null=True)
    
    class Meta:
        db_table = 'method_analyte_jn_stg_vw'
        managed = False
        
class MethodStgSummaryVw(models.Model):
    
    revision_id = models.IntegerField()
    revision_information = models.CharField(max_length=100)
    revision_flag = models.IntegerField(null=True)
    method_id = models.IntegerField(primary_key=True)
    source_method_identifier = models.CharField(max_length=30)
    method_descriptive_name = models.CharField(max_length=250)
    method_official_name = models.CharField(max_length=250)
    method_source_id = models.IntegerField()
    source_citation_id = models.IntegerField()
    brief_method_summary = models.CharField(max_length=4000)
    scope_and_application = models.CharField(max_length=2000, blank=True)
    media_name = models.CharField(max_length=30)
    dl_type_id = models.IntegerField(null=True)
    dl_note = models.CharField(max_length=2000, blank=True)
    applicable_conc_range = models.CharField(max_length=300, blank=True)
    conc_range_units = models.CharField(max_length=20, blank=True)
    interferences = models.CharField(max_length=3000, blank=True)
    method_source_contact = models.CharField(max_length=450, blank=True)
    qc_requirements = models.CharField(max_length=2000, blank=True)
    link_to_full_method = models.CharField(max_length=240, blank=True)
    sample_handling = models.CharField(max_length=3000, blank=True)
    max_holding_time = models.CharField(max_length=300, blank=True)
    sample_prep_methods = models.CharField(max_length=100, blank=True)
    relative_cost_id = models.IntegerField(null=True)
    method_source = models.CharField(max_length=20)
    method_source_name = models.CharField(max_length=150)
    method_source_url = models.CharField(max_length=200, blank=True)
    precision_descriptor_notes = models.CharField(max_length=3000, blank=True)
    method_subcategory_id = models.IntegerField()
    method_category = models.CharField(max_length=50)
    method_subcategory = models.CharField(max_length=40)
    dl_type = models.CharField(max_length=11, blank=True)
    dl_type_description = models.CharField(max_length=50, blank=True)
    source_citation_name = models.CharField(max_length=450, blank=True)
    source_citation = models.CharField(max_length=30)
    source_citation_information = models.CharField(max_length=1500, blank=True)
    relative_cost_symbol = models.CharField(max_length=7, blank=True)
    relative_cost = models.CharField(max_length=40, blank=True)
    method_type_desc = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'method_stg_summary_vw'
        managed = False
        
class RegulationRef(models.Model):
    regulation_id = models.IntegerField(primary_key=True)
    regulation = models.CharField(max_length=10)
    regulation_name = models.CharField(max_length=60)
    reg_location = models.CharField(max_length=30)
    reg_location_2 = models.CharField(max_length=30, blank=True)
    
    class Meta:
        db_table = 'regulation_ref'
        managed = False
        
class RegQueryVW(models.Model):
    
    conc_range_units = models.CharField(max_length=20, blank=True)
    interferences = models.CharField(max_length=3000, blank=True)
    analyte_method_id = models.IntegerField()
    qc_requirements = models.CharField(max_length=2000, blank=True)
    false_positive_value = models.IntegerField(null=True)
    false_negative_value = models.IntegerField(null=True)
    link_to_full_method = models.CharField(max_length=240, blank=True)
    sample_handling = models.CharField(max_length=3000, blank=True)
    max_holding_time = models.CharField(max_length=300, blank=True)
    sample_prep_methods = models.CharField(max_length=100, blank=True)
    relative_cost_id = models.IntegerField(null=True)
    method_source = models.CharField(max_length=20)
    method_source_name = models.CharField(max_length=150)
    method_source_url = models.CharField(max_length=200, blank=True)
    method_subcategory_id = models.IntegerField()
    method_category = models.CharField(max_length=50)
    method_subcategory = models.CharField(max_length=40)
    dl_type = models.CharField(max_length=11, blank=True)
    dl_type_description = models.CharField(max_length=50, blank=True)
    source_citation_name = models.CharField(max_length=450, blank=True)
    source_citation = models.CharField(max_length=30)
    source_citation_information = models.CharField(max_length=1500, blank=True)
    relative_cost_symbol = models.CharField(max_length=7, blank=True)
    relative_cost = models.CharField(max_length=40, blank=True)
    revision_id = models.IntegerField(primary_key=True)
    revision_information = models.CharField(max_length=100)
    revision_flag = models.IntegerField(blank=True)
    mimetype = models.CharField(max_length=50, blank=True)
    #mydoc
    regulation_name = models.CharField(max_length=60)
    regulation = models.CharField(max_length=10)
    reg_location = models.CharField(max_length=30)
    reg_location_2 = models.CharField(max_length=30, blank=True)
    regulation_note = models.CharField(max_length=200, blank=True)
    analyte_revision_id = models.IntegerField()
    dl_units = models.CharField(max_length=20)
    dl_value = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    sub_dl_value = models.CharField(max_length=40, blank=True)
    instrumentation_id = models.IntegerField()
    analyte_id = models.IntegerField()
    accuracy = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    sub_accuracy = models.CharField(max_length=40, blank=True)
    accuracy_order = models.IntegerField(null=True)
    accuracy_units = models.CharField(max_length=40, blank=True)
    precision = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    sub_precision = models.CharField(max_length=40, blank=True)
    precision_units = models.CharField(max_length=30, blank=True)
    precision_descriptor_notes = models.CharField(max_length=300, blank=True)
    prec_acc_conc_used = models.DecimalField(max_digits=21, decimal_places=6, null=True)
    instrumentation = models.CharField(max_length=20)
    instrumentation_description = models.CharField(max_length=200)
    analyte_code = models.CharField(max_length=20)
    analyte_name = models.CharField(max_length=240)
    preferred = models.IntegerField(null=True)
    method_id = models.IntegerField()
    source_method_identifier = models.CharField(max_length=30)
    method_descriptive_name = models.CharField(max_length=250)
    method_official_name = models.CharField(max_length=250)
    method_source_id = models.IntegerField()
    source_citation_id = models.IntegerField()
    dl_units_description = models.CharField(max_length=60, blank=True)
    precision_units_description = models.CharField(max_length=100, blank=True)
    accuracy_units_description = models.CharField(max_length=50, blank=True)
    brief_method_summary = models.CharField(max_length=4000)
    scope_and_application = models.CharField(max_length=200, blank=True)
    media_name = models.CharField(max_length=30)
    dl_type_id = models.IntegerField(null=True)
    dl_note = models.CharField(max_length=2000, blank=True)
    applicable_conc_range = models.CharField(max_length=300, blank=True)
    
    class Meta:
        db_table = 'reg_query_vw'
        managed = False
        
class RegulatoryMethodReport(models.Model):
    
    analyte_name = models.CharField(max_length=240, primary_key=True)
    epa_id = models.IntegerField(null=True)
    epa_rev_id = models.IntegerField(null=True)
    epa = models.CharField(max_length=143, blank=True)
    standard_methods_id = models.IntegerField(null=True)
    standard_methods_rev_id = models.IntegerField(null=True)
    standard_methods = models.CharField(max_length=143, blank=True)
    usgs_id = models.IntegerField(null=True)
    usgs_rev_id = models.IntegerField(null=True)
    usgs = models.CharField(max_length=143, blank=True)
    astm_id = models.IntegerField(null=True)
    astm_rev_id = models.IntegerField(null=True)
    astm = models.CharField(max_length=143, blank=True)
    other_id = models.IntegerField(null=True)
    other_rev_id = models.IntegerField(null=True)
    other = models.CharField(max_length=143, blank=True)
    
    class Meta:
        db_table = 'regulatory_method_report'
        managed = False
        
class RelativeCostRef(models.Model):
    
    relative_cost_id = models.IntegerField(primary_key=True) 
    relative_cost_symbol = models.CharField(max_length=7)
    relative_cost = models.CharField(max_length=40)
    cost_effort_key = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'relative_cost_ref'
        managed = False

class StatisticalItemType(models.Model):
    
    stat_item_index = models.IntegerField(primary_key=True)
    item = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'statistical_item_type'
        ordering = ['item']

    def __unicode__(self):
        return self.item
    
class StatisticalAnalysisType(models.Model):
    
    stat_analysis_index = models.IntegerField(primary_key=True)
    analysis_type = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'statistical_analysis_type'
        ordering = ['analysis_type']

    def __unicode__(self):
        return self.analysis_type
        
class StatisticalSourceType(models.Model):
   
    stat_source_index = models.IntegerField(primary_key=True) 
    source = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'statistical_source_type'
        ordering = ['source']

    def __unicode__(self):
        return self.source

class StatisticalDesignObjective(models.Model):
    
    stat_design_index = models.IntegerField(primary_key=True)
    objective = models.CharField(max_length=200)

    class Meta:
        db_table = 'statistical_design_objective'
        ordering = ['objective']
        
    def __unicode__(self):
        return self.objective

class StatisticalTopics(models.Model):
    
    stat_topic_index = models.IntegerField(primary_key=True)
    stat_special_topic = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'statistical_topics'
        ordering = ['stat_special_topic']
        
    def __unicode__(self):
        return self.stat_special_topic
        
class CitationTypeRef(models.Model):
    citation_type_id = models.IntegerField(primary_key=True)
    citation_type = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'citation_type_ref'
        ordering = ['citation_type']
        
    def __unicode__(self):
        return self.citation_type        

COMPLEXITY_CHOICES = [
    (u'Low', u'Low'),
    (u'Medium', u'Medium'),
    (u'High', u'High')]

LEVEL_OF_TRAINING_CHOICES = [
    (u'Basic', u'Basic'),
    (u'Intermediate', u'Intermediate'),
    (u'Advanced', u'Advanced')]


class StatisticalMethodManager(models.Manager):
    '''Extends the Manager class to provide a query set that returns a data which has a citation type of Statistic.
    '''
    
    def get_query_set(self):
        return super(StatisticalMethodManager, self).get_query_set().filter(citation_type__citation_type__exact='Statistic')
        
class SourceCitationRef(models.Model):
    
    source_citation_id = models.IntegerField(primary_key=True) 
    source_citation = models.CharField(max_length=30, 
                                       blank=False,
                                       verbose_name='source abbreviation',
                                       help_text='Enter an acronym or shortened name')
    source_citation_name = models.CharField(max_length=450, 
                                            verbose_name="citation", 
                                            help_text="Description of source citation")
    source_citation_information = models.CharField(max_length=1500)
    insert_person = models.ForeignKey(User, null=True)
    insert_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    approve_flag = models.CharField(max_length=1, 
                                    choices=[('N', 'No'), ('Y', 'Yes')], 
                                    default='N')
    title = models.CharField(max_length=450, 
                             help_text='Citation\'s full title')
    author = models.CharField(max_length=450, 
                              help_text='Citation author(s)')
    abstract_summary = models.CharField(max_length=2000, 
                                        blank=True, 
                                        verbose_name='abstract/summary statement', 
                                        help_text='Abstract/summary statement')
    table_of_contents = models.CharField(max_length=1000, 
                                         blank=True, 
                                         help_text="Major headings")
    link = models.CharField(max_length=450, 
                            blank=True, 
                            help_text="Link to source citation")
    notes = models.CharField(max_length=600, 
                             blank=True, 
                             verbose_name='special notes or comments', 
                             help_text='Special notes or comments about this citation')
    publication_year = models.IntegerField(max_length=4, 
                                           null=True, 
                                           help_text='Publication year')
    citation_type = models.ForeignKey(CitationTypeRef)
    source_organization = models.ForeignKey(MethodSourceRef, 
                                            null=True, 
                                            blank=True, 
                                            help_text="Source organization")
    country = models.CharField(max_length=100, 
                               blank=True, 
                               help_text='Country where published')
    complexity = models.CharField(max_length=10, 
                                  choices=COMPLEXITY_CHOICES, 
                                  help_text='Relatively speaking...')
    level_of_training = models.CharField(max_length=20, 
                                         choices=LEVEL_OF_TRAINING_CHOICES, 
                                         help_text='Your level of statistical training')
    item_type = models.ForeignKey(StatisticalItemType, 
                                  null=True, 
                                  help_text='The form of the item, e.g., book, journal article, web site, etc.')
    item_type_note = models.CharField(max_length=50, 
                                      blank=True, 
                                      verbose_name='if other type selected, please describe', 
                                      help_text='Add a description if item type is other')
    analysis_types = models.ManyToManyField(StatisticalAnalysisType, 
                                            null=True, 
                                            help_text='Do you already have the data or are you designing a monitoring program?')
    sponser_types = models.ManyToManyField(StatisticalSourceType, 
                                           null=True, 
                                           verbose_name='publication source type', 
                                           help_text='What type of organization produced this item?')
    sponser_type_note = models.CharField(max_length=50, 
                                         blank=True, 
                                         verbose_name='if other source selected, please describe', 
                                         help_text='Add a description if publication source type is other')
    media_emphasized = models.ManyToManyField(MediaNameDOM, 
                                              null=True, 
                                              help_text='Water, air, biological tissue, other?')
    media_emphasized_note = models.CharField(max_length=50, 
                                             blank=True, 
                                             verbose_name='If other media selected, please describe', 
                                             help_text="Add a description if media emphasized is other")
    subcategory = models.CharField(max_length=150, 
                                   blank=True, 
                                   verbose_name='media subcategory', 
                                   help_text='Enter a media subcategory if appropriate')
    design_objectives = models.ManyToManyField(StatisticalDesignObjective, 
                                               null=True, 
                                               help_text = 'What water resources information need are you addressing, e.g., time trends, standards evaluation, etc.?')
    special_topics = models.ManyToManyField(StatisticalTopics, 
                                            null=True, 
                                            blank=True,
                                            help_text='Looking for help with nondetect, autocorrelation, data collected using sensor, etc.?')
    
    objects = models.Manager()
    stat_methods = StatisticalMethodManager()
    
    class Meta:
        db_table = 'source_citation_ref'
        managed = False

    def __unicode__(self):
        return self.source_citation
        