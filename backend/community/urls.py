from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BadgeViewSet,
    UserBadgeViewSet,
    FeedbackViewSet,
    MentorshipConnectionViewSet,
    CommunityDataViewSet
)

router = DefaultRouter()
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'user-badges', UserBadgeViewSet, basename='user-badge')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'mentorships', MentorshipConnectionViewSet, basename='mentorship')
router.register(r'data', CommunityDataViewSet, basename='community-data')

urlpatterns = [
    path('', include(router.urls)),
]
