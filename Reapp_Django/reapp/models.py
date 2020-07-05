from django.db import models

# Create your models here.

class Search(models.Model):
	name       = models.CharField(max_length=200)
	price      = models.IntegerField(default=0)
	image_link = models.CharField(max_length=500)

	def __str__(self):
		return self.name

class Product(models.Model):
	search = models.ForeignKey(Search, on_delete=models.CASCADE)
	prod_name   = models.CharField(max_length=200)
	prod_price  = models.IntegerField(default=0)
	prod_image  = models.CharField(max_length=500)
