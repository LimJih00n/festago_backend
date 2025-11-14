from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BookmarkViewSet, ReviewViewSet

# Events 라우터 (기본 경로)
event_router = DefaultRouter()
event_router.register(r'', EventViewSet, basename='event')

# Bookmarks & Reviews 라우터 (별도 경로)
other_router = DefaultRouter()
other_router.register(r'bookmarks', BookmarkViewSet, basename='bookmark')
other_router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(other_router.urls)),
    path('', include(event_router.urls)),
]
