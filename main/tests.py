from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from .models import JobPost


class JobPostImageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="employer", password="secret123")

    def test_post_job_with_image_uploads_and_saves_image(self):
        image_file = BytesIO()
        Image.new("RGB", (120, 80), color="blue").save(image_file, format="PNG")
        image_file.seek(0)

        uploaded_image = SimpleUploadedFile(
            "job-cover.png",
            image_file.read(),
            content_type="image/png",
        )

        self.client.force_login(self.user)
        response = self.client.post(
            "/main/post_job",
            {
                "title": "Senior Backend Engineer",
                "company": "JobyQuo",
                "type": "Full-Time",
                "location": "Remote",
                "salary": "$120k",
                "level": "Senior Level",
                "skill": "Django, Python",
                "description": "Build the next great product.",
                "image": uploaded_image,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        job = JobPost.objects.get(title="Senior Backend Engineer")
        self.assertTrue(job.image)
        self.assertIn("job-cover.png", job.image.name)
