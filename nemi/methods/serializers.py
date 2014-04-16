from rest_framework import serializers

from .models import MethodVW

class MethodVWSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = MethodVW
        
        fields = ('method_id',
                  'source_method_identifier',
                  'method_descriptive_name',
                  'method_official_name',
                  'sam_complexity',
                  'brief_method_summary',
                  'scope_and_application',
                  'media_name',
                  'dl_note',
                  'applicable_conc_range',
                  'conc_range_units',
                  'interferences',
                  'qc_requirements',
                  'link_to_full_method',
                  'sample_handling',
                  'max_holding_time',
                  'sample_prep_methods',
                  'precision_descriptor_notes',
                  'waterbody_type',
                  'matrix',
                  'method_source',
                  'method_source_name',
                  'method_source_contact',
                  'method_source_url',
                  'method_category',
                  'method_subcategory',
                  'dl_type',
                  'dl_type_description',
                  'source_citation_name',
                  'source_citation',
                  'source_citation_information',
                  'instrumentation',
                  'instrumentation_description',
                  'method_type_desc',
                  'publication_year',
                  'author',
                  'collected_sample_amt_ml',
                  )