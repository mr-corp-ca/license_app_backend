from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/', include('user_management_app.urls')),
    path('api/courses/', include('course_management_app.urls')),
    path('api/utils/', include('utils_app.urls')),
    path('api/dashboard/', include('admin_dashboard.urls')),
    path('api/timing/', include('timing_slot_app.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)