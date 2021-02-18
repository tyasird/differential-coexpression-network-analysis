from django.db import models
from django.utils import timezone

# Create your models here.
class DiffCoExpression(models.Model):

    cancer_id = models.IntegerField(blank=True, null=True)
    input_excel = models.TextField(blank=True, null=True)
    healthy_sample = models.IntegerField(blank=True, null=True)
    disease_sample = models.IntegerField(blank=True, null=True)
    healthy_pcritic = models.TextField(blank=True, null=True)
    disease_pcritic = models.TextField(blank=True, null=True)
    healthy_normality_pvalue = models.TextField(blank=True, null=True)
    disease_normality_pvalue = models.TextField(blank=True, null=True)
    healthy_co_expression = models.JSONField(blank=True, null=True)
    disease_co_expression = models.JSONField(blank=True, null=True)
    healthy_diff_co_expression = models.JSONField(blank=True, null=True)
    disease_diff_co_expression = models.JSONField(blank=True, null=True)
    timestamp = models.DateField(default=timezone.now,blank=True, null=True)

    def publish(self):
        self.timestamp = timezone.now()
        self.save()

    def __str__(self):
        return str(self.id) + "_" + str(self.timestamp)


class Network(models.Model):


    diff_coexp = models.ForeignKey(DiffCoExpression,null=True,on_delete=models.CASCADE)

    #diff_coexp_id = models.IntegerField(blank=True)
    type = models.IntegerField(blank=True,null=True) #0 Disease
    mcode = models.JSONField(blank=True, null=True)
    timestamp = models.DateField(default=timezone.now,blank=True, null=True)

    def publish(self):
        self.timestamp = timezone.now()
        self.save()

    def __str__(self):
        return str(self.id) + "_" + str(self.timestamp)
