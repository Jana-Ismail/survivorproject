from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from survivorapi.views import login_user, register_user, SeasonLogs

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"season-logs", SeasonLogs, "season-log")

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user),
    path('admin/', admin.site.urls),
]

