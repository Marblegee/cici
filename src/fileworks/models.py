from django.db import models

# Create your models here.


class DfUpload(models.Model):
    ptss = models.CharField(max_length=200)
    time = models.CharField(max_length=200)
    exp = models.CharField(max_length=200)
    t2ies = models.CharField(max_length=200)
    cset = models.CharField(max_length=200)

    def __str__(self):
        return 'Dataset' + str(self.id)
