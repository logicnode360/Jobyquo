from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
    path("post_job", views.post_job, name="post_job"),
    path('profile/', views.profile, name='profile'),
    path('my_applicants/', views.my_applicants, name='my_applicants'),
    path('apply/', views.apply, name='apply'),
    path('approve-application/<int:application_id>/', views.approve_application, name='approve_application'),
    path('reject-application/<int:application_id>/', views.reject_application, name='reject_application'),
    path('chat/<int:application_id>/', views.chat_room, name='chat_room'),
    path('notifications/', views.notifications, name='notifications'),
    path('chats/', views.my_chats, name='my_chats'),
    path('manage_job/', views.manage_job, name='manage_job'),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )