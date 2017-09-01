
from django.core.validators import RegexValidator
from django.db import models

class HelpContent(models.Model):

    field_name = models.CharField(max_length=30,
                                  unique=True,
                                  validators=[RegexValidator(regex='^[a-zA-Z0-9]\w+[a-zA-Z0-9]$',
                                                             message='Invalid: can only contain alphanumerics and underscores, however no leading or trailing underscores'),],
                                  help_text="Should match the database column name if referencing a table element, otherwise should be unique.")
    label = models.CharField(max_length=75,
                             help_text="Text to show on the website for this field.")
    tooltip = models.CharField(max_length=100,
                               blank=True,
                               help_text="Optional text to show in when hovering over the label.")
    description = models.CharField(max_length=4000,
                                   blank=True,
                                   help_text="Optional text to show in a popup help dialog.")

    class Meta:
        db_table = 'dom_help_content'
        managed = True

    def __unicode__(self):
        return self.field_name
