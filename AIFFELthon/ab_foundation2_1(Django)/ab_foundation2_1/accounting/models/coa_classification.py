from django.db import models

class COAClassification(models.Model):
    code  = models.CharField(max_length=20, unique=True)
    group = models.CharField(max_length=50, blank=True, null=True)
    label = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["code"]
        verbose_name = "COA Classification"
        verbose_name_plural = "COA Classifications"

    def __str__(self):
        return f"{self.code} – {self.label or self.group}"
