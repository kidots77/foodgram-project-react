from django.db import models


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    measurement_inut = models.CharField(max_length=50)

    class Meta:
        ordering = ('name', )

    def __str__(self):
        return self.name
