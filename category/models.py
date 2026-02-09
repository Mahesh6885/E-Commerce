from django.db import models

class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug=models.CharField(max_length=100,unique=True)
    description=models.CharField(max_length=200)
    cat_image=models.ImageField(upload_to="photos/category",blank=True)

    def __str__(self):
        return self.category_name