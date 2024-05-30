import os
from datetime import datetime
from django.db import models


# Create your models here.
class UploadImages(models.Model):
    image = models.ImageField()
    uploaded_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Generate new filename
        extension = self.image.name.split('.')[-1]  # get the file extension
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{now}.{extension}"

        # Update image field with the new filename
        self.image.name = os.path.join('post_images', new_filename)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.image.name

class OverviewInsight(models.Model):
    platform_id = models.CharField(max_length=6, primary_key=True)
    platform = models.CharField(max_length=30)
    no_of_page_reach = models.IntegerField(default=0)
    no_of_page_likes = models.IntegerField(default=0)
    no_of_page_followers = models.IntegerField(default=0)
    no_of_published_post = models.IntegerField(default=0)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Overview Insight: {self.platform}"

class PostInsight(models.Model):
    post_id = models.CharField(max_length=100)
    platform = models.CharField(max_length=30)
    post_content = models.TextField()
    no_of_likes = models.IntegerField(default=0)
    no_of_comments = models.IntegerField(default=0)
    no_of_shares = models.IntegerField(default=0)

    def __str__(self):
        return f"Post Insight: {self.post_id}"