from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('partners', views.PartnerViewSet, basename='partner')
router.register('applications', views.ApplicationViewSet, basename='application')
router.register('messages', views.MessageViewSet, basename='message')
router.register('analytics', views.AnalyticsViewSet, basename='analytics')
router.register('uploads', views.ImageUploadViewSet, basename='upload')
router.register('notifications', views.NotificationViewSet, basename='notification')
router.register('drafts', views.ApplicationDraftViewSet, basename='draft')
router.register('bookmarks', views.FestivalBookmarkViewSet, basename='bookmark')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('festivals/', views.PartnerFestivalListView.as_view(), name='festivals'),
]
