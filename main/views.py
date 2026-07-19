from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models

from .models import ChatMessage, JobPost, ApplyJob, Profile
from django.template.loader import render_to_string
from django.http import HttpResponse

# Create your views here.


@login_required
def dashboard(request):
    jobs = JobPost.objects.all().order_by("-id")
    user = request.user
    defult_profile_pic = user.username[0].upper()
    user_applications = ApplyJob.objects.filter(applicant=request.user).select_related('job') if request.user.is_authenticated else ApplyJob.objects.none()

    return render(request, "main/dashboard.html", {"jobs": jobs, "user": user, "defult_profile_pic": defult_profile_pic, "user_applications": user_applications})


def post_job(request):
    # Support edit via ?edit=<id> or POST with edit_id
    edit_id = request.GET.get("edit") or request.POST.get("edit_id")
    job_obj = None

    if edit_id:
        job_obj = get_object_or_404(JobPost, id=edit_id, user=request.user)

    if request.method == "POST":
        title = request.POST.get("title")
        company = request.POST.get("company")
        type_ = request.POST.get("type")
        location = request.POST.get("location")
        salary = request.POST.get("salary")
        level = request.POST.get("level")
        skill = request.POST.get("skill")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        if job_obj:
            # update existing
            job_obj.title = title
            job_obj.company = company
            job_obj.type = type_
            job_obj.location = location
            job_obj.salary = salary
            job_obj.level = level
            job_obj.skill = skill
            job_obj.description = description
            if image:
                job_obj.image = image
            job_obj.save()
            messages.success(request, "Job post updated.")
            return redirect("manage_job")

        # create new
        JobPost.objects.create(
            user=request.user,
            title=title,
            company=company,
            type=type_,
            location=location,
            salary=salary,
            level=level,
            skill=skill,
            description=description,
            image=image,
        )
        messages.success(request, "Job posted successfully.")
        return redirect("dashboard")

    return render(request, "main/post_job.html", {"job": job_obj})


@login_required
def profile(request):
    user = request.user
    jobs = user.jobpost_set.all()
    applications = ApplyJob.objects.filter(applicant=user).select_related("job", "job__user").order_by("-applied_date")
    profile, created = Profile.objects.get_or_create(user=user)
    if request.method == "POST":
        if request.FILES.get("profile_pic"):
            profile.profile_pic = request.FILES["profile_pic"]
            profile.save()

        username = request.POST.get("username")
        email = request.POST.get("email")

        if username:
            user.username = username
        if email:
            user.email = email

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")
    defult_profile_pic = user.username[0].upper()

    return render(request, "main/profile.html", {"jobs": jobs, "user": user, "defult_profile_pic": defult_profile_pic, "profile": profile, "applications": applications})


@login_required
def my_applicants(request):
    job_posts = JobPost.objects.filter(user=request.user)
    applicants = ApplyJob.objects.filter(job__in=job_posts).select_related("applicant", "job").order_by("-applied_date")

    return render(
        request,
        "main/my_applicants.html",
        {"applicants": applicants},
    )


@login_required
def manage_job(request):
    user = request.user
    jobs = JobPost.objects.filter(user=user).order_by('-id')
    return render(request, "main/manage_job.html", {"jobs": jobs})


@login_required
def delete_job(request, job_id):
    job = get_object_or_404(JobPost, id=job_id, user=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job post deleted.")
        return redirect("manage_job")
    return render(request, "main/confirm_delete.html", {"job": job})


@login_required
def approve_application(request, application_id):
    application = get_object_or_404(ApplyJob, id=application_id, job__user=request.user)
    application.status = "approved"
    application.save(update_fields=["status"])
    messages.success(request, f"{application.applicant.username} is now approved to chat for {application.job.title}.")
    return redirect("my_applicants")


@login_required
def reject_application(request, application_id):
    application = get_object_or_404(ApplyJob, id=application_id, job__user=request.user)
    application.status = "rejected"
    application.save(update_fields=["status"])
    messages.info(request, f"{application.applicant.username} was marked as rejected for {application.job.title}.")
    return redirect("my_applicants")


@login_required
def apply(request, job_id=None):
    job_id = job_id or request.GET.get("job_id") or request.POST.get("job_id")
    job = get_object_or_404(JobPost, id=job_id) if job_id else None

    if request.method == "POST":
        if not job:
            job = get_object_or_404(JobPost, id=request.POST.get("job_id"))

        if ApplyJob.objects.filter(job=job, applicant=request.user).exists():
            messages.warning(request, "You already applied for this job.")
            return redirect("dashboard")

        resume = request.FILES.get("resume")
        cover_letter = request.POST.get("cover_letter", "").strip()

        if not resume:
            messages.error(request, "Please upload your resume before submitting.")
            return render(request, "main/apply.html", {"job": job})

        ApplyJob.objects.create(
            job=job,
            applicant=request.user,
            resume=resume,
            cover_letter=cover_letter,
            status="pending",
        )
        messages.success(request, "Applied successfully.")
        return redirect("dashboard")

    return render(request, "main/apply.html", {"job": job})


@login_required
def chat_room(request, application_id):
    application = get_object_or_404(ApplyJob, id=application_id)
    is_participant = request.user in (application.applicant, application.job.user)

    if not is_participant:
        return HttpResponseForbidden("You are not allowed to chat on this application.")

    if application.status != "approved":
        messages.warning(request, "This applicant must be approved before chat is available.")
        return redirect("my_applicants")

    messages_list = ChatMessage.objects.filter(application=application).order_by("created_at")

    # mark messages as read for the current user when viewing the chat
    ChatMessage.objects.filter(application=application, receiver=request.user, is_read=False).update(is_read=True)

    if request.method == "POST":
        text = request.POST.get("message", "").strip()
        if text:
            receiver = application.job.user if request.user == application.applicant else application.applicant
            ChatMessage.objects.create(
                application=application,
                sender=request.user,
                receiver=receiver,
                text=text,
            )

        if request.headers.get("HX-Request"):
            return render(request, "main/chat_messages.html", {"messages": ChatMessage.objects.filter(application=application).order_by("created_at"), "application": application})

        return redirect("chat_room", application_id=application.id)

    if request.headers.get("HX-Request"):
        return render(request, "main/chat_messages.html", {"messages": messages_list, "application": application})

    return render(request, "main/chat_room.html", {"application": application, "messages": messages_list})


@login_required
def notifications(request):
    # count unread messages for current user
    unread = ChatMessage.objects.filter(receiver=request.user, is_read=False).count()
    html = render_to_string("main/_notifications.html", {"unread": unread})
    return HttpResponse(html)


@login_required
def my_chats(request):
    # approved applications where the user is a participant
    chats = ApplyJob.objects.filter(status="approved").filter(models.Q(applicant=request.user) | models.Q(job__user=request.user)).select_related("job", "applicant", "job__user").order_by("-applied_date")
    return render(request, "main/my_chats.html", {"chats": chats})