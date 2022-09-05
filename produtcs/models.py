from email.policy import default
from operator import mod
from turtle import update
from venv import create
from django.db import models

# Create your models here.

class Product(models.Model):
    name=models.CharField(max_length=120)
    image=models.ImageField(upload_to='produtcs',default="no_pitcure.jpg")
    price=models.FloatField(help_text='in US dollars $')
    created = models.DateTimeField(auto_created=True)
    update=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}--{self.created.strftime('%d/%m/%y')}"