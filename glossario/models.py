from django.db import models


class Termo(models.Model):
    termo = models.CharField(max_length=100)
    significado = models.TextField()
    slug = models.SlugField()