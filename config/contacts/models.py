from django.db import models


class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20,unique=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    class Meta:
        ordering = ['name']
    