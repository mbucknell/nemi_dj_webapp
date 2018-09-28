from django.db import models

from common.models import SourceCitationRef, Method


class ProtocolMethodRel(models.Model):
    protocol_method_id = models.IntegerField(primary_key=True)
    source_citation = models.ForeignKey(SourceCitationRef,
                                        models.CASCADE,
                                        db_column='source_citation_id')
    method = models.ForeignKey(Method, models.CASCADE, db_column='method_id')

    class Meta:
        db_table = 'protocol_method_rel'
        managed = False
