
from django.contrib.auth.models import User
from django.db import models

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
        
    def __unicode__(self):
        return self.definition_name

class MethodSubcategoryRef(models.Model):
    
    method_subcategory_id = models.IntegerField(primary_key=True)
    method_category = models.CharField(max_length=50)
    method_subcategory = models.CharField(max_length=40)
    
    class Meta:
        db_table = 'method_subcategory_ref'
        managed = False
        
    def __unicode__(self):
        return self.method_subcategory
        
        
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
    
class StatisticalItemType(models.Model):
    
    stat_item_index = models.IntegerField(primary_key=True)
    item = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'statistical_item_type'
        ordering = ['item']

    def __unicode__(self):
        return self.item
    
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
        db_table = u'media_name_dom'
        ordering = ['media_name']
        managed = False
        
    def __unicode__(self):
        return self.media_name.lower().title()

        
class StatisticalSourceType(models.Model):
   
    stat_source_index = models.IntegerField(primary_key=True) 
    source = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'statistical_source_type'
        ordering = ['source']

    def __unicode__(self):
        return self.source
    

class SourceCitationRefAbstract(models.Model):
    ''' Abstract model which abstracts the common fields for the three flavors of source citation ref tables.'''
    
    source_citation = models.CharField(max_length=30) 
    source_citation_name = models.CharField(max_length=450) 
    source_citation_information = models.CharField(max_length=1500, 
                                                   blank=True)
    title = models.CharField(max_length=450)
    author = models.CharField(max_length=450) 
    table_of_contents = models.CharField(max_length=1000)
    link = models.CharField(max_length=450, blank=True) 
    publication_year = models.IntegerField(max_length=4, 
                                           null=True)
    country = models.CharField(max_length=100, blank=True)
    item_type = models.ForeignKey(StatisticalItemType)
    item_type_note = models.CharField(max_length=50, 
                                      blank=True)
    sponser_type_note = models.CharField(max_length=50, 
                                         blank=True)
    insert_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)
    insert_person_name = models.CharField(max_length=50, 
                                          blank=True)
    
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.source_citation
    
    
class SourceCitationOnlineRef(SourceCitationRefAbstract):
    
    source_citation_id = models.AutoField(primary_key=True)
                
    class Meta:
        db_table = u'source_citation_online_ref'
        managed = False


class SourceCitationStgRef(SourceCitationRefAbstract):
    
    source_citation_id = models.IntegerField(primary_key=True)
              
    class Meta:
        db_table = u'source_citation_stg_ref'
        managed = False
      
        
class SourceCitationRef(SourceCitationRefAbstract):
    
    source_citation_id = models.IntegerField(primary_key=True)
    
    class Meta:
        db_table = u'source_citation_ref'
        managed = False


class PublicationSourceRelAbstract(models.Model):
    
    source = models.ForeignKey(StatisticalSourceType,
                               db_column='statisticalsourcetype_id')
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return unicode(self.source)

    
class PublicationSourceRelStg(PublicationSourceRelAbstract):
    
    source_citation_ref_id = models.IntegerField(db_column='sourcecitationref_id')
    
    class Meta:
        db_table = u'publication_source_rel_stg'
        ordering = ['source']
        
        
class PublicationSourceRel(PublicationSourceRelAbstract):
    
    source_citation_ref = models.ForeignKey(SourceCitationRef,
                                            db_column='sourcecitationref_id')
    
    class Meta:
        db_table = u'publication_source_rel'
        ordering = ['source']
    
        
class DlRef(models.Model):
    
    dl_type_id = models.IntegerField(primary_key=True, unique=True)
    dl_type = models.CharField(max_length=11, unique=True)
    dl_type_description = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = u'dl_ref'
        managed = False
        
    def __unicode__(self):
        return self.dl_type
    

class DlUnitsDom(models.Model):
    
    dl_units = models.CharField(max_length=20, primary_key=True, unique=True)
    dl_units_description = models.CharField(max_length=60, blank=True)
    class Meta:
        db_table = u'dl_units_dom'
        managed = False
        
    def __unicode__(self):
        return self.dl_units


class RelativeCostRef(models.Model):

    relative_cost_id = models.IntegerField(primary_key=True) 
    relative_cost_symbol = models.CharField(max_length=7)
    relative_cost = models.CharField(max_length=40)
    cost_effort_key = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'relative_cost_ref'
        managed = False
        
    def __unicode__(self):
        return self.relative_cost
    

class InstrumentationRef(models.Model):
    
    instrumentation_id = models.IntegerField(primary_key=True)
    instrumentation = models.CharField(max_length=20)
    instrumentation_description = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'instrumentation_ref'
        managed = False
        
    def __unicode__(self):
        return self.instrumentation

class WaterbodyTypeRef(models.Model):
    
    waterbody_type_id = models.IntegerField(unique=True, primary_key=True)
    waterbody_type_desc = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = u'waterbody_type_ref'
        managed = False
        
    def __unicode__(self):
        return self.waterbody_type_desc


class MethodTypeRef(models.Model):
    
    method_type_id = models.IntegerField(primary_key=True)
    method_type_desc = models.CharField(max_length=100)
    
    class Meta:
        db_table = u'method_type_ref'
        managed = False

    def __unicode__(self):
        return self.method_type_desc
    

COMPLEXITY_CHOICES = [
    (u'Low', u'Low'),
    (u'Medium', u'Medium'),
    (u'High', u'High')]

LEVEL_OF_TRAINING_CHOICES = [
    (u'Basic', u'Basic'),
    (u'Intermediate', u'Intermediate'),
    (u'Advanced', u'Advanced')]


class StatisticalMethodManager(models.Manager):
    '''Extends the Manager class to provide a query set that returns a data which has a method category of "STATISTICAL"
    '''
    
    def get_query_set(self):
        return super(StatisticalMethodManager, self).get_query_set().filter(method_subcategory__method_category__exact='STATISTICAL')


class MethodAbstract(models.Model):    
    method_subcategory = models.ForeignKey(MethodSubcategoryRef, 
                                           null=True, 
                                           blank=True)
    method_source = models.ForeignKey(MethodSourceRef, 
                                      null=True,
                                      blank=True)
    source_method_identifier = models.CharField(max_length=30, 
                                                unique=True)
    method_descriptive_name = models.CharField(max_length=450, 
                                               blank=True)
    method_official_name = models.CharField(max_length=250)
    media_name = models.ForeignKey(MediaNameDOM, 
                                   null=True, 
                                   db_column='media_name', 
                                   blank=True)
    brief_method_summary = models.CharField(max_length=4000)
    scope_and_application = models.CharField(max_length=2000, 
                                             blank=True)
    dl_type = models.ForeignKey(DlRef, 
                                null=True, 
                                blank=True)
    dl_note = models.CharField(max_length=2000, 
                               blank=True)
    applicable_conc_range = models.CharField(max_length=300, 
                                             blank=True)
    conc_range_units = models.ForeignKey(DlUnitsDom, 
                                         null=True, 
                                         db_column='conc_range_units', 
                                         blank=True)
    interferences = models.CharField(max_length=3000, 
                                     blank=True)
    qc_requirements = models.CharField(max_length=2000, 
                                       blank=True)
    sample_handling = models.CharField(max_length=3000, 
                                       blank=True)
    max_holding_time = models.CharField(max_length=300, 
                                        blank=True)
    sample_prep_methods = models.CharField(max_length=100, 
                                           blank=True)
    relative_cost = models.ForeignKey(RelativeCostRef, 
                                      null=True, 
                                      blank=True)
    link_to_full_method = models.CharField(max_length=240, 
                                           blank=True)
    insert_date = models.DateField(null=True, 
                                   blank=True)
    insert_person_name = models.CharField(max_length=50, 
                                          blank=True)
    last_update_date = models.DateField(null=True, 
                                        blank=True)
    last_update_person_name = models.CharField(max_length=50, 
                                               blank=True)
    approved = models.CharField(max_length=1, 
                                default='N')
    approved_date = models.DateField(null=True, 
                                     blank=True)
    instrumentation = models.ForeignKey(InstrumentationRef, 
                                        null=True, 
                                        blank=True)
    precision_descriptor_notes = models.CharField(max_length=3000, 
                                                  blank=True)
    rapidity = models.CharField(max_length=30, 
                                blank=True)
    waterbody_type = models.ForeignKey(WaterbodyTypeRef, 
                                       null=True, 
                                       db_column='waterbody_type',
                                        blank=True)
    matrix = models.CharField(max_length=12, 
                              blank=True)
    technique = models.CharField(max_length=50, 
                                 blank=True)
    screening = models.CharField(max_length=8, 
                                 blank=True)
    reviewer_name = models.CharField(max_length=100, 
                                     blank=True)
    regs_only = models.CharField(max_length=1, 
                                 default='N')
    method_type = models.ForeignKey(MethodTypeRef)
    cbr_only = models.CharField(max_length=1, 
                                default='N')
    etv_link = models.CharField(max_length=120, 
                                blank=True)
    collected_sample_amt_ml = models.CharField(max_length=10,
                                               blank=True)
    collected_sample_amt_g = models.CharField(max_length=10, 
                                              blank=True)
    liquid_sample_flag = models.CharField(max_length=1, 
                                          blank=True)
    analysis_amt_ml = models.CharField(max_length=10, 
                                       blank=True)
    analysis_amt_g = models.CharField(max_length=10, 
                                      blank=True)
    ph_of_analytical_sample = models.CharField(max_length=10, 
                                               blank=True)
    calc_waste_amt = models.DecimalField(null=True, 
                                         max_digits=7, 
                                         decimal_places=2, 
                                         blank=True)
    quality_review_id = models.CharField(max_length=100, 
                                         blank=True)
    pbt = models.CharField(max_length=1, 
                           blank=True)
    toxic = models.CharField(max_length=1, 
                             blank=True)
    corrosive = models.CharField(max_length=1, 
                                 blank=True)
    waste = models.CharField(max_length=1, 
                             blank=True)
    assumptions_comments = models.CharField(max_length=2000, 
                                            blank=True)
    sam_complexity = models.CharField(max_length=10,  
                                      blank=True,
                                      choices=COMPLEXITY_CHOICES)
    level_of_training = models.CharField(max_length=20, 
                                         blank=True,
                                         choices=LEVEL_OF_TRAINING_CHOICES) 
    media_emphasized_note = models.CharField(max_length=50, 
                                             blank=True) 
    media_subcategory = models.CharField(max_length=150, 
                                         blank=True) 
    notes = models.CharField(max_length=4000, blank=True)

    objects = models.Manager()
    stat_methods = StatisticalMethodManager() # Use this manager to retrieve SAMS methods only
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return self.source_method_identifier
        
    def get_insert_user(self):
        ''' Returns the User object for the person who inserted the object. If the user can not be found 'None' is returned.
        '''
        user_qs = User.objects.filter(username=self.insert_person_name)
        if user_qs:
            return user_qs[0]
        else:
            return User(username='Unknown')
                            
class MethodOnline(MethodAbstract):
    
    method_id = models.AutoField(primary_key=True)
    source_citation_id = models.IntegerField()
    comments = models.CharField(max_length=2000, 
                                blank=True)
    ready_for_review = models.CharField(max_length=1, 
                                        default='N')
    insert_person_name2 = models.CharField(max_length=100, 
                                           blank=True) # Don't use this field for SAMS methods
    delete_after_load = models.CharField(max_length=1)
    wqsa_category_cd = models.IntegerField(null=True, 
                                           blank=True)
    
    class Meta:
        db_table = u'method_online'
        managed = False
        
        
class MethodStg(MethodAbstract):
    
    method_id = models.IntegerField(primary_key=True)
    source_citation_id = models.IntegerField()
    comments = models.CharField(max_length=2000, 
                                blank=True)
    ready_for_review = models.CharField(max_length=1, 
                                        default='N')
    date_loaded = models.DateField()
    wqsa_category_cd = models.IntegerField(null=True, 
                                           blank=True)
    
    class Meta:
        db_table = u'method_stg'
        managed = False
        
        
class Method(MethodAbstract):
    
    method_id = models.IntegerField(primary_key=True)
    source_citation = models.ForeignKey(SourceCitationRef)
    date_loaded = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = u'method'
        managed = False
 
 
class StatisticalAnalysisType(models.Model):
    
    stat_analysis_index = models.IntegerField(primary_key=True)
    analysis_type = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'statistical_analysis_type'
        ordering = ['analysis_type']

    def __unicode__(self):
        return self.analysis_type
    

class StatisticalDesignObjective(models.Model):
    
    stat_design_index = models.IntegerField(primary_key=True)
    objective = models.CharField(max_length=200)

    class Meta:
        db_table = u'statistical_design_objective'
        ordering = ['objective']
        
    def __unicode__(self):
        return self.objective
    

class StatisticalTopics(models.Model):
    
    stat_topic_index = models.IntegerField(primary_key=True)
    stat_special_topic = models.CharField(max_length=200)
    
    class Meta:
        db_table = u'statistical_topics'
        ordering = ['stat_special_topic']
        
    def __unicode__(self):
        return self.stat_special_topic
    
    
class StatAnalysisRelAbstract(models.Model):
    
    analysis_type = models.ForeignKey(StatisticalAnalysisType, db_column='statisticalanalysistype_id')
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return unicode(self.analysis_type)
    
        
class StatAnalysisRelStg(StatAnalysisRelAbstract):
    
    method_id = models.IntegerField()
    
    class Meta:
        db_table = u'stat_analysis_rel_stg'
        ordering = ['analysis_type']
        
        
class StatAnalysisRel(StatAnalysisRelAbstract):
    
    method = models.ForeignKey(Method)
    
    class Meta:
        db_table = u'stat_analysis_rel'
        ordering = ['analysis_type']
        
    
class StatDesignRelAbstract(models.Model):
    
    design_objective = models.ForeignKey(StatisticalDesignObjective, db_column='statisticaldesignobjective_id')
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return unicode(self.design_objective)
    
class StatDesignRelStg(StatDesignRelAbstract):
    
    method_id = models.IntegerField()
    
    class Meta:
        db_table = u'stat_design_rel_stg'
        ordering = ['design_objective']
        
        
class StatDesignRel(StatDesignRelAbstract):
    
    method = models.ForeignKey(Method)
    
    class Meta:
        db_table = u'stat_design_rel'
        ordering = ['design_objective']

        
class StatTopicRelAbstract(models.Model):
    
    topic = models.ForeignKey(StatisticalTopics, db_column='statisticaltopics_id')
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return unicode(self.topic)
    
        
class StatTopicRelStg(StatTopicRelAbstract):
    
    method_id = models.IntegerField()
    
    class Meta:
        db_table = u'stat_topic_rel_stg'
        ordering = ['topic']
        
        
class StatTopicRel(StatTopicRelAbstract):
    
    method = models.ForeignKey(Method)
    
    class Meta:
        db_table = u'stat_topic_rel'
        ordering = ['topic']
        
        
class StatMediaRelAbstract(models.Model):
    
    media_name = models.ForeignKey(MediaNameDOM, db_column='medianamedom_id')
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return unicode(self.media_name)
    
        
class StatMediaRelStg(StatMediaRelAbstract):
    
    method_id = models.IntegerField()
    
    class Meta:
        db_table = u'stat_media_rel_stg'
        ordering = ['media_name']
        
        
class StatMediaRel(StatMediaRelAbstract):
    
    method = models.ForeignKey(Method)
    
    class Meta:
        db_table = u'stat_media_rel'
        ordering = ['media_name']
  

class WebFormDefinition(models.Model):
    
    field_name = models.CharField(max_length=32, 
                                  unique=True)
    label = models.CharField(max_length=64,
                             blank=True)
    tooltip = models.CharField(max_length=200,
                               blank=True)
    help_text = models.CharField(max_length=1000,
                                 blank=True)
    
    def __unicode__(self):
        return self.field_name
    
    class Meta:
        db_table = u'web_form_definition'
        