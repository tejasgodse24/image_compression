import pandas as pd
import requests
from PIL import Image 
import io, os
from django.conf import settings
from celery import shared_task
from imgcompress.models import *
from django.db import transaction
import time
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

@shared_task
def handle_csv_img(file_json, request_id):

    request_obj = ProcessingRequest.objects.get(request_id = request_id)

    try:
        df = pd.read_json(io.StringIO(file_json))
        
        if "Input Image Urls" not in df.columns or "Product Name" not in df.columns or "S. No." not in df.columns:
            request_obj.status = ProcessingRequest.Status.FAILED
            request_obj.status_reason = "One of column Input Image Urls, Product Name, S. No. not exists in file"
            request_obj.save()
            return


        df = df.dropna(subset=["Input Image Urls"])
        df["Input Image Urls"] = df["Input Image Urls"].astype(str)

        # Split image URLs into lists
        df["Input Image Urls"] = df["Input Image Urls"].apply(lambda x: x.split(","))

        # Convert to dictionary - {(Product Name, srno): [list of image URLs]}
        product_images_dict = df.set_index(["Product Name", "S. No."])["Input Image Urls"].to_dict()

        for (prod, srno), urls in product_images_dict.items():
            with transaction.atomic():
                product_obj = Product.objects.create(product_name=prod, srno=srno, request=request_obj)
            
            for url in urls:
                compress_img(url, product_obj)


        # save output csv with compressed img urls
        csv_path = generate_output_csv(request_id)

        # change status of request
        request_obj.status = ProcessingRequest.Status.COMPLETED
        request_obj.csv_output_url = csv_path
        request_obj.status_reason = "File Processing Completed Successfully"
        request_obj.save()

        # call webhook 
        webhook_call(request_id)

    except Exception as e:
        # change status of request
        request_obj.status = ProcessingRequest.Status.FAILED
        request_obj.status_reason = str(e)
        request_obj.save()



def compress_img(img_url, product_obj):

    img_obj = ProductImage.objects.create(product = product_obj, input_img_url = img_url)

    try:
        response = requests.get(img_url, stream=True)
        if response.status_code != 200:
            img_obj.compressed_img_url = ""
            img_obj.save()
        
        image = Image.open(io.BytesIO(response.content))

        img_io = io.BytesIO()
        image.save(img_io, format="JPEG", quality=50, optimize=True)
        img_io.seek(0)

        # Upload to S3
        s3_path = f"compressed_images/compressed_img_{str(img_obj.img_id)}.jpg"
        default_storage.save(s3_path, ContentFile(img_io.getvalue()))

        # Save the S3 URL to the model
        img_obj.compressed_img_url = default_storage.url(s3_path)
        img_obj.save()

    except Exception as e:
        img_obj.compressed_img_url = ""
        img_obj.save()
        print("error: ", e)



def generate_output_csv(request_id):
    try:
        request_obj = ProcessingRequest.objects.get(request_id=request_id)
        products = request_obj.product.all()

        data = []

        for product in products:
            input_images = [img.input_img_url for img in product.image.all()]
            output_images = [img.compressed_img_url for img in product.image.all()]

            data.append({
                "S. No.": product.srno,
                "Product Name": product.product_name,
                "Input Image Urls": ", ".join(input_images),
                "Output Image Urls": ", ".join(output_images),
            })

        df = pd.DataFrame(data)

        # Convert df to csv
        csv_io = io.StringIO()
        df.to_csv(csv_io, index=False)
        csv_io.seek(0)

        # Upload to S3
        s3_path = f"processed_csv/output_{request_id}.csv"
        default_storage.save(s3_path, ContentFile(csv_io.getvalue()))

        return default_storage.url(s3_path)

    except Exception as e:
        print("Error generating CSV:", e)
        return ""
    

from django.conf import settings
def webhook_call(request_id):
    webhook_url = settings.WEBHOOK_URL  # Replace with the actual webhook URL
    payload = {
        "request_id": str(request_id)
    }
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()  # Raise an error if the request fails
    except Exception as e:
        print(f"Failed to send webhook: {e}")