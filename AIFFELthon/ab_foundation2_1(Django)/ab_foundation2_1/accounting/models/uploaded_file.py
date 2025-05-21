from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

class UploadedFile(models.Model):
    original_filename = models.CharField(max_length=255)
    original_filepath = models.FileField(upload_to='invoices/original_files/')
    abf_filename = models.CharField(max_length=50, blank=True, default="")
    new_filename = models.CharField(max_length=255, blank=True, null=True)
    new_filepath = models.FileField(upload_to='invoices/converted_files/', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    parsed_json = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.abf_filename} ({self.original_filename})"
