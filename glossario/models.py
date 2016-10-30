from django.db import models
from django.utils.six import python_2_unicode_compatible


@python_2_unicode_compatible
class Termo(models.Model):
    termo = models.CharField(max_length=100)
    significado = models.TextField()
    slug = models.SlugField()

    class Meta:
        ordering = ('termo',)

    def __str__(self):
        return self.termo