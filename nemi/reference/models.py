from django.db import models


YES_NO_CHOICES = (
    ('N', 'No'),
    ('Y', 'Yes')
)


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


class CbrAdvice(models.Model):
    advice_id = models.IntegerField(primary_key=True)
    analyte_category = models.CharField(max_length=1000)
    analyte_category_intro = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cbr_advice'


class AnalyteRef(models.Model):
    analyte_id = models.IntegerField(primary_key=True)

    analyte_code = models.CharField(unique=True, max_length=20)
    analyte_type = models.CharField(max_length=100, blank=True, null=True)
    analyte_cbr = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        verbose_name='analyte CBR',
        choices=YES_NO_CHOICES)
    usgs_pcode = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name='USGS pcode')
    analyte_code_cbr = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='analyte code CBR',
        choices=YES_NO_CHOICES)

    cbr_analyte_category = models.ForeignKey(CbrAdvice, models.DO_NOTHING, db_column='cbr_analyte_category', blank=True, null=True)
    cbr_analyte_intro = models.CharField(max_length=4000, blank=True, null=True)

    data_entry_name = models.CharField(max_length=50, blank=True, null=True)
    data_entry_date = models.DateField(blank=True, null=True)
    update_name = models.CharField(max_length=50, blank=True, null=True)
    update_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'analyte_ref'
        verbose_name = 'analyte'

    def __str__(self):
        return self.analyte_code


class AnalyteCodeRel(models.Model):
    analyte_code_id = models.AutoField(primary_key=True)
    analyte = models.ForeignKey(AnalyteRef, models.DO_NOTHING)

    analyte_code = models.CharField(max_length=20, blank=True, null=True)
    analyte_name = models.CharField(max_length=240)
    preferred = models.IntegerField(
        blank=True,
        null=True,
        choices=((None, 'No'), (-1, 'Yes'))
    )
    analyte_type = models.CharField(max_length=50, blank=True, null=True)

    data_entry_name = models.CharField(max_length=20, blank=True, null=True)
    data_entry_date = models.DateField(blank=True, null=True)
    update_name = models.CharField(max_length=50, blank=True, null=True)
    update_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'analyte_code_rel'
        unique_together = (('analyte', 'analyte_name'),)
        verbose_name = 'analyte and code management'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.analyte_name


class DlRef(models.Model):
    dl_type_id = models.AutoField(primary_key=True)
    dl_type = models.CharField(max_length=11, verbose_name='detection limit type')
    dl_type_description = models.CharField(max_length=50, verbose_name='description')
    data_entry_date = models.DateField(blank=True, null=True)
    update_name = models.CharField(max_length=50, blank=True, null=True)
    update_date = models.DateField(blank=True, null=True)
    data_entry_name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dl_ref'
        unique_together = (('dl_type', 'dl_type_description'),)
        verbose_name = 'detection limit type'

    def __str__(self):
        return '%s - %s' % (self.dl_type, self.dl_type_description)


class DlUnitsDom(models.Model):
    dl_units = models.CharField(primary_key=True, max_length=20, verbose_name='detection limit unit')
    dl_units_description = models.CharField(max_length=60, blank=True, null=True, verbose_name='description')
    data_entry_name = models.CharField(max_length=50, blank=True, null=True)
    data_entry_date = models.DateField(blank=True, null=True)
    update_name = models.CharField(max_length=50, blank=True, null=True)
    update_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dl_units_dom'
        verbose_name = 'detection limit unit'

    def __str__(self):
        return self.dl_units



class InstrumentationRef(models.Model):
    instrumentation_id = models.IntegerField(primary_key=True)
    instrumentation = models.CharField(max_length=20)
    instrumentation_description = models.CharField(unique=True, max_length=200)
    data_entry_name = models.CharField(max_length=50, blank=True, null=True)
    data_entry_date = models.DateField(blank=True, null=True)
    update_name = models.CharField(max_length=50, blank=True, null=True)
    update_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'instrumentation_ref'
        unique_together = (('instrumentation', 'instrumentation_description'),)
        verbose_name = 'instrumentation'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s: %s' % (self.instrumentation, self.instrumentation_description)


class MethodSourceRef(models.Model):
    method_source_id = models.IntegerField(primary_key=True)
    method_source = models.CharField(max_length=20)
    method_source_url = models.CharField(max_length=200, blank=True, null=True)
    method_source_name = models.CharField(max_length=150)
    method_source_contact = models.CharField(max_length=450, blank=True, null=True)
    method_source_email = models.CharField(max_length=100, blank=True, null=True)
    data_entry_name = models.CharField(max_length=50, blank=True, null=True)
    data_entry_date = models.DateField(blank=True, null=True)
    update_name = models.CharField(max_length=50, blank=True, null=True)
    update_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'method_source_ref'
        unique_together = (('method_source', 'method_source_name'),)
        verbose_name = 'method source'

    def __str__(self):
        return '%s: %s' % (self.method_source, self.method_source_name)
