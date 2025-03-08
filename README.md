# Asynchronous Image Compression using Celery

### Tech Stack
Django, Django Rest Framework, SqLite3 (Can use database external services like RDS/NeonDB), Celery, Redis (as Message Broker),

## Deployment Stack
AWS EC2, AWS S3 Bucket, Nginx, GitHub, Gunicorn, Supervisor(for celery configuration), Ubuntu, Hostinger Domain Name(Subdomain)


## Installation Instructions

### Prerequisites:
• Python 3.10 and above
• SqLite3 Database (default with Python Django - no need to install it explicitly)


### Steps to run the application
1) Clone the Project
   
2) Start Django Server for Backend
   1) Create Virtual Env
      - create virtual environment using `python -m venv venv` in root folder.
      - activate that virtualenv using `venv/scripts/activate`(Windows) / `source venv/bin/activate`(Ubuntu)
   2) Do some prerequisit stuff
      - install all required dependencies using `pip install -r requirements.txt`
      - create superuser using `python manage.py createsuperuser` if you want to.
      - make migrations using `python manage.py makemigrations`
      - apply migrations using `python manage.py migrate`
    3) Start Server
       - start django dev server using `python manage.py runserver`


### Database Schema:
![alt text](https://imgcompress-bkt.s3.ap-south-1.amazonaws.com/DBSchema.png)


### Low-Level Design(LLD):
[text](https://imgcompress-bkt.s3.ap-south-1.amazonaws.com/img_compression.drawioFinal.pdf)


### API Documentation:
[text](https://documenter.getpostman.com/view/31971917/2sAYdoF7M5)

