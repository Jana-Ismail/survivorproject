from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from survivorapi.views import login_user, register_user, SeasonLogs, Seasons, Tribes, Survivors, SurvivorTribes, SurvivorNotes

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"season-logs", SeasonLogs, "season-log")
router.register(r"seasons", Seasons, "season")
router.register(r"tribes", Tribes, "tribe")
router.register(r"survivors", Survivors, "survivor")
router.register(r"survivor-tribes", SurvivorTribes, "survivor-tribes")
router.register(r"survivor-notes", SurvivorNotes, "survivor-note")

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user),
    path('admin/', admin.site.urls),
]

