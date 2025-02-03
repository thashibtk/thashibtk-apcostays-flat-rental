from django.db import models


class RegisterDb(models.Model):
    UserID = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=100, null=True, blank=True)
    Email = models.EmailField(max_length=100, null=True, blank=True)
    Password = models.CharField(max_length=100, null=True, blank=True)
    ConfirmPassword = models.CharField(max_length=100, null=True, blank=True)
    Location = models.CharField(max_length=100, null=True, blank=True)
    Phone = models.CharField(max_length=15, null=True, blank=True)  

    def __str__(self):
        return self.Email

class Rental(models.Model):
    title = models.CharField(max_length=255)
    property_type = models.CharField(max_length=50)
    rooms = models.IntegerField()
    location = models.CharField(max_length=255)
    rent = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    verified = models.BooleanField(default=False)

    # Add ForeignKey relationship
    owner = models.ForeignKey(RegisterDb, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class RentalImage(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='rentals/')

    def __str__(self):
        return f"Image for {self.rental.title}"
