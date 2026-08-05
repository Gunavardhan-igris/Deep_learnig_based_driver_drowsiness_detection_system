from django.db import models


class AdminModel(models.Model):

    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username

    class Meta:
        db_table = "AdminLogin"