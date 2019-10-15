from django.db import models

# Create your models here.


class loginTimes(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    dateTime = models.DateTimeField()
    times = models.IntegerField()
    effective = models.BooleanField()

    class Meta:
        ordering = ['id']
        db_table = 'loginTimes'
