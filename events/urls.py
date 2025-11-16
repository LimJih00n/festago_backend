from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, BookmarkViewSet

# 이벤트 라우터
event_router = DefaultRouter()
event_router.register(r'', EventViewSet, basename='event')

# 북마크 라우터
bookmark_router = DefaultRouter()
bookmark_router.register(r'', BookmarkViewSet, basename='bookmark')

urlpatterns = [
    path('bookmarks/', include(bookmark_router.urls)),
    path('', include(event_router.urls)),
]
