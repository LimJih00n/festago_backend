from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BookmarkViewSet

# Events와 Bookmarks 라우터
router = DefaultRouter()
router.register(r'', EventViewSet, basename='event')
router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')

urlpatterns = [
    path('', include(router.urls)),
]
