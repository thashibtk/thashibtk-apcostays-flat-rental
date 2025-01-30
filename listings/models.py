from django.db import models

# Create your models here.
# class Listing(models.Model):
#     title = models.CharField(max_length=200)
#     description = models.TextField()
#     location = models.CharField(max_length=100)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     available_from = models.DateField()
#     image = models.ImageField(upload_to='listing_images/')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title


class RegisterDb(models.Model):
    UserID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100, null=True, blank=True)
    Email = models.EmailField(max_length=100, null=True, blank=True)
    Password = models.CharField(max_length=100, null=True, blank=True)
    ConfirmPassword = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.Email

