from django.db import models
from django.contrib.auth.models import User


class JobPost(models.Model):
    JOB_TYPES = [
        ("Full-Time", "Full-Time"),
        ("Part-Time", "Part-Time"),
        ("Remote", "Remote"),
        ("Hybrid", "Hybrid"),
        ("Contract", "Contract"),
        ("Internship", "Internship"),
    ]
    EXP_LEVEL = [
        ("Entry Level", "Entry Level"),
        ("Mid Level", "Mid Level"),
        ("Senior Level", "Senior Level"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=JOB_TYPES)
    location = models.CharField(max_length=300)
    salary = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=EXP_LEVEL)
    skill = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="job_images/", null=True, blank=True)

    def __str__(self):
        return f"{self.title} (#{self.id})"


class ApplyJob(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    job = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="resumes/")
    cover_letter = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    applied_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "applicant")

    def __str__(self):
        return f"{self.applicant.username} -> {self.job.title}"


class ChatMessage(models.Model):
    application = models.ForeignKey(ApplyJob, on_delete=models.CASCADE, related_name="chat_messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_chat_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_chat_messages")
    text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to="profile_pics/", null=True, blank=True)

    def __str__(self):
        return self.user.username