from rest_framework.response import Response 
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import pandas as pd
from imgcompress.tasks import handle_csv_img
from io import BytesIO
from imgcompress.models import *
import os


# Create your views here.

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_file(request):
    if 'file' not in request.FILES:
        return Response({"request_id": "0", 'message': "No File Uploaded"}, status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_size_mb = round(uploaded_file.size  / (1024 * 1024), 2)
    # print("file_size_mb", file_size_mb)

    try:
        if not file_name.endswith(('.csv', '.xls', '.xlsx')):
            return Response({"request_id": "0", 'message': "Unsupported file format. Use CSV or Excel."}, status=status.HTTP_400_BAD_REQUEST)

        if file_size_mb > 10:
            return Response({"request_id": "0", 'message': "Upload file less than 10 mb"}, status=status.HTTP_400_BAD_REQUEST)


        obj = ProcessingRequest.objects.create()

        # convert file into jsin
        file_bytes = uploaded_file.read()
        if file_name.endswith('.csv'):
            df = pd.read_csv(BytesIO(file_bytes))
        else:
            df = pd.read_excel(BytesIO(file_bytes))

        file_json = df.to_json(orient='records') 

        # Sending JSON instead of file because celery tasks only accepts json serializable objects
        handle_csv_img.delay(file_json=file_json, request_id=obj.request_id)  
        # handle_csv_img(file_json=file_json, request_id=obj.request_id)  

        return Response({"request_id":obj.request_id, 'message': 'File Processing Started...'}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"request_id": "0", 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def check_status(request, request_id):
    try:
        request_obj = ProcessingRequest.objects.get(request_id = request_id)
    except Exception as e:
        return Response({"request_id": "0", "status": "Request Not Found", "message":"Request Not Found" }, status=404)
    
    return Response({ "request_id": str(request_obj.request_id), "status": request_obj.status, "message":request_obj.status_reason})


@api_view(['POST'])
def webhook_reciever(request):
    try:
        request_id = request.data.get("request_id")
        if not request_id:
            return Response({ "data": {}, "message": "request_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            request_obj = ProcessingRequest.objects.get(request_id=request_id)
        except Exception as e:
            return Response({ "data": {}, "message": "Invalid request_id"}, status=status.HTTP_404_NOT_FOUND)


        if request_obj.status != ProcessingRequest.Status.COMPLETED:
            return Response({ "data": {"request_id":str(request_obj.request_id), "status": request_obj.status}, "message": "Process not yet completed"}, status=status.HTTP_200_OK)

        return Response(
            { "data": {"request_id": str(request_obj.request_id), "status": request_obj.status, "csv_download_url": request_obj.csv_output_url}, 
              "message": "Processing completed successfully"
            }
        )
    
    except Exception as e:
        return Response({ "data": {}, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)