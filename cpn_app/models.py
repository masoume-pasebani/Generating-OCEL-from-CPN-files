from django.conf import settings
from django.db import models

class UploadedCPNFile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    file = models.FileField(upload_to='cpn_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file.name} uploaded by {self.user.username}"

class GeneratedOCEL(models.Model):
    cpn_file = models.ForeignKey(UploadedCPNFile, on_delete=models.CASCADE)
    generated_file = models.FileField(upload_to='ocel_files/')
    created_at = models.DateTimeField(auto_now_add=True)


