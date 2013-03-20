from django.db import models

class NewsItem(models.Model):
    
    headline = models.CharField(max_length=300)
    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)
    
    def __unicode__(self):
        return str(self.pk)
    
    class Meta:
        ordering = ['-created']
        db_table = 'news_item'