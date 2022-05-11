from django.db import models

# Create your models here.
# class Contact(models.Model):
#     ptss = models.IntegerField()
#     time = models.IntegerField()
#     exp = models.IntegerField()
#     t2ies = models.IntegerField()
#     cset = models.IntegerField()

#     def __str__(self):
#         return f'{self.y} {self.x1}'


class DfUpload(models.Model):
    ptss = models.IntegerField()
    time = models.IntegerField()
    exp = models.IntegerField()
    t2ies = models.IntegerField()
    cset = models.IntegerField()

    def __str__(self):
        return 'Dataset' + str(self.id)
