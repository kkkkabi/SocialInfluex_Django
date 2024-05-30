from django.db import models
from django.contrib.auth import get_user_model
import uuid #generate unique id for post
from datetime import datetime #get datetime of 

# Everytime we use this user, it will be currently logging in user
User = get_user_model()

# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE) #foreign key that is linking to that model
    id_user = models.IntegerField() #ID of the user to access the profile, interger
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, max_length=255)
    # profileimg = models.ImageField(upload_to='profile_images', default= 'blank_profile.png') #profile Image

    def __str__(self):
        return self.user.username

