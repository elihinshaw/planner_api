from django.db import models

class CustomUser(models.Model):
    username = models.CharField(unique=True, max_length=30)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username
