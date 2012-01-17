''' This module contain the model class defintions for the tables and views
that are used to implement the NEMI search pages. All tables and views are read
only and therefore have managed set to Fasle in each model's Meta data.
'''

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
    dl_type_id = models.IntegerField()
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
    analyte_id = models.IntegerField(primary_key=True)
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
        
class MediaNameDOM(models.Model):
    
    media_name = models.CharField(max_length=30, primary_key=True)
    media_id = models.IntegerField(null=True)
    
    class Meta:
        db_table = 'media_name_dom'
        managed = False
        
class MethodSourceRef(models.Model):
    
    method_source_id = models.IntegerField(primary_key=True)
    method_source = models.CharField(max_length=20)
    method_source_url = models.CharField(max_length=200, blank=True)
    method_source_name = models.CharField(max_length=150)
    mehtod_source_contact = models.CharField(max_length=450, blank=True)
    method_source_email = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'method_source_ref'
        managed = False
        
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
        
class relativeCostRef(models.Model):
    
    relative_cost_id = models.IntegerField(primary_key=True) 
    relative_cost_symbol = models.CharField(max_length=7)
    relative_cost = models.CharField(max_length=40)
    cost_effort_key = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'relative_cost_ref'
        managed = False

class sourceCitationRef(models.Model):
    
    ANALYSIS_CHOICES = (
        (u'1', u'Monitoring program design'),
        (u'2', u'Analysis of exsisting data'),
        (u'3', u'Both')
    )
    
    ITEM_TYPE = (
        (u'1', u'Report / Guidance Document'),
        (u'2', u'Journal Article'),
        (u'3', u'Book'),
        (u'4', u'Book Chapter / Section'),
        (u'5', u'Downloadable Software'),
        (u'6', u'Online Calculator'),
        (u'7', u'Other')
    )
    
    COMPLEXITY_CHOICES = (
        (13, u'Low'),
        (14, u'Medium'),
        (15, u'High')
    )
     
    source_citation_id = models.IntegerField(primary_key=True, max_length=11) 
    source_citation = models.CharField(max_length=30)
    source_citation_name = models.CharField(max_length=450)
    source_citation_information = models.CharField(max_length=1500)
    insert_person_name = models.CharField(max_length=25)
    insert_date = models.DateField()
    title = models.CharField(max_length=450)
    author = models.CharField(max_length=450)
    abstract_summary = models.CharField(max_length=2000)
    table_of_contents = models.CharField(max_length=1000)
    link = models.CharField(max_length=450)
    notes = models.CharField(max_length=450)
    item_type = models.IntegerField(max_length=11, choices=ITEM_TYPE)
    analysis_type = models.IntegerField(max_length=11, choices=ANALYSIS_CHOICES)
    complexity = models.IntegerField(max_length=11, choices=COMPLEXITY_CHOICES)
    publication_year = models.IntegerField(max_length=4)
    citation_type = models.IntegerField()
    source_organization = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'source_citation_ref'
        managed = False

#    def __unicode__(self):
#         return '%s' % (self.get_complexity_display())

class statTopicsRel(models.Model):
    
    TOPICS_CHOICES = (
         (u'1', u'Handling non-detects'),
         (u'2', u'Identifying outliers'),
         (u'3', u'Evaluating whether data follows a certain (e.g. normal) distribution'),
         (u'4', u'Assessing and managing autocorrlation'),
         (u'5', u'Measurements taken using a water quality sensor'),
         (u'6', u'Characterizing the uncertainty of an estimate')
     )
    
    topics_pk = models.IntegerField(primary_key=True)
#    source_citation_id = models.IntegerField()
    source_citation_id = models.ForeignKey(sourceCitationRef)
    stat_topic_index = models.IntegerField(choices=TOPICS_CHOICES)
    
    class Meta:
        db_table = 'stat_topics_rel'
        managed = False

class statSourceRel(models.Model):
   
    SOURCE_CHOICES = (
         (u'1', u'Journal'),
         (u'2', u'Non-governmental Organization'),
         (u'3', u'Government Agency (Federal, USA)'),
         (u'4', u'Government Agency (State, USA)'),
         (u'5', u'Government Agency (Tribal, NA)'),
         (u'6', u'Academic Institution'),
         (u'7', u'Regional Organization'),
         (u'8', u'Other'),
         (u'9', u'International Government Agency'),
         (u'10', u'Industry')
                    
     )
   
    source_pk = models.IntegerField(primary_key=True)
#    source_citation_id = models.IntegerField()
    source_citation_id = models.ForeignKey(sourceCitationRef)
    stat_source_index = models.IntegerField(choices=SOURCE_CHOICES)    
    
    class Meta:
        db_table = 'stat_source_rel'
        managed = False    

class statMediaRel(models.Model):
    
    MEDIA_CHOICES = (
        (u'1', u'Water'),
        (u'2', u'Agricultural Products'),
        (u'3', u'Air'),
        (u'4', u'Animal Tissue'),
        (u'5', u'Soil / Sediment'),
        (u'6', u'Various'),
        (u'7', u'Other'),
        (u'8', u'Surface Water'),
        (u'9', u'Ground Water'),
        (u'10', u'Sediment'),
        (u'11', u'Dredged Material'),
        (u'12', u'Biological')                    
     )    
    
    media_pk = models.IntegerField(primary_key=True)
#    source_citation_id = models.IntegerField()
    source_citation_id = models.ForeignKey(sourceCitationRef)
    stat_media_index = models.IntegerField(choices=MEDIA_CHOICES)    
    
    class Meta:
        db_table = 'stat_media_rel'
        managed = False

class statDesignRel(models.Model):
    
    DESIGN_CHOICES = (
         (u'1', u'Summarize data in terms of means, medians, distributions, percentiles'),
         (u'2', u'Evaluate compliance with a threshold value'),
         (u'3', u'Characterize temporal trends (long-term, annual, seasonal)'),
         (u'4', u'Characterize  spatial trends'),
         (u'5', u'Design or evaluate data from a probability survey'),
         (u'6', u'Evaluate relationships among variables'),
         (u'7', u'Estimate river flow statistics'),
         (u'8', u'Estimate downstream loadings of chemicals or suspended materials'),
         (u'9', u'Develop source identification/apportionment information'),
         (u'10', u'Determine flow-adjusted chemical concentrations'),
         (u'11', u'Derive water quality threshold values'),
         (u'12', u'Estimate volumes of contaminated soil, sediment, or other material'),
         (u'13', u'Compare a location to a reference site'),
         (u'14', u'Compare control and experimental treatments'),
         (u'15', u'Evaluate "continuous" data (e.g., measurements collected hourly or more often)'),
         (u'16', u'Evaluate biological data (e.g., benthic macroinvertebrates, fish, diatoms)'),
         (u'17', u'Evaluate bioassay/bioaccumulation/toxicity data'),
         (u'18', u'Estimate concentrations at unsampled locations')
     ) 
    
    design_pk = models.IntegerField(primary_key=True)
#    source_citation_id = models.IntegerField()
    stat_design_index = models.IntegerField(choices=DESIGN_CHOICES)
    source_citation_id = models.ForeignKey(sourceCitationRef)
    
    class Meta:
        db_table = 'stat_design_rel'
        managed = False
#########################################################################################################
#  Maybe don't need these:
class statisticalDesignObjective(models.Model):
    
    stat_design_index = models.IntegerField(primary_key=True)
    objective = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'statistical_design_objective'
        managed = False
        
class statisticalAnalysisType(models.Model):
    
    stat_analysis_index = models.IntegerField(primary_key=True)
    analysis_type = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'statistical_analysis_type'
        managed = False
        
class statisticalTopics(models.Model):
      
    stat_topic_index = models.IntegerField(primary_key=True)
    stat_special_topic = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'statistical_topics'
        managed = False

class statisticalSourceType(models.Model):
    
    stat_source_index = models.IntegerField(primary_key=True)
    source = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'statistical_source_type'
        managed = False

class statisticalItemType(models.Model):
    
    stat_item_index = models.IntegerField(primary_key=True)
    item = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'statistical_item_type'
        managed = False




        

        