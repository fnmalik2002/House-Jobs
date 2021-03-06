from django.db import models
from django.db.models.deletion import CASCADE
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class Payments(models.Model):
    # jobpost = models.ForeignKey(JobPost, on_delete=CASCADE)
    # payment_for_month = models.CharField(max_length=200)
    payment_amount = models.IntegerField(default=0)
    payment_date = models.DateTimeField('payment date', auto_now_add=True)
    payment_note = models.CharField(max_length=200, default=None)
    payment_uid = models.CharField(max_length=200, default=None)

    # def __str__(self):
    #     return str(self.id)

class JobPost(models.Model):
    job_title = models.CharField(max_length=200)
    publish_date = models.DateTimeField('date published', auto_now_add=True)
    job_is_template = models.BooleanField(default=False)
    job_detail = models.CharField(max_length=200)
    job_price = models.IntegerField(default=0)
    job_taken = models.BooleanField(default=False)
    job_under_review = models.BooleanField(default=False)
    job_passed_review = models.BooleanField(default=False)
    job_taken_date = models.DateTimeField('date job taken', null=True, blank=True)
    job_done = models.BooleanField(default=False)
    job_done_date = models.DateTimeField('date job completed', null=True, blank=True)
    job_taker = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='job_user')
    job_creator = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='job_author')
    job_rejected_by_admin = models.BooleanField(default=False)
    job_expired = models.BooleanField(default=False)
    job_paid = models.BooleanField(default=False)
    job_payment_id = models.ForeignKey(Payments, on_delete=models.CASCADE, null=True, blank=True, related_name='job_payment_id')
    
    def __str__(self):
        return self.job_title
    
    def was_published_recently(self):
        return self.publish_date >= timezone.now() - timezone.timedelta(days=1)


