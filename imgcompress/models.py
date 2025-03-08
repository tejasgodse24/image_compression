from django.db import models
import uuid

# Create your models here.




class ProcessingRequest(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED" , "Failed"
        
    request_id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS
    )
    status_reason = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    csv_output_url = models.URLField(null=True, blank=True)


class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=100, null=True, blank=True)
    srno = models.PositiveIntegerField(null=True, blank=True)
    request = models.ForeignKey(ProcessingRequest, on_delete=models.CASCADE, related_name="product")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ProductImage(models.Model):
    img_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="image")
    input_img_url = models.URLField(null=True, blank=True)
    compressed_img_url = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
