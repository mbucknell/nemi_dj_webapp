from django.db import models


class AccuracyUnitsDom(models.Model):
    accuracy_units = models.CharField(primary_key=True, max_length=50)
    accuracy_units_description = models.CharField(max_length=50, blank=True, null=True)
    data_entry_name = models.CharField(max_length=50, blank=True, null=True)
    data_entry_date = models.DateField(blank=True, null=True)
    update_name = models.CharField(max_length=50, blank=True, null=True)
    update_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accuracy_units_dom'
        verbose_name = 'accuracy unit'

    def __str__(self):
        return self.accuracy_units
