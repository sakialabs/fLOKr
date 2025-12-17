from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BadgeViewSet,
    UserBadgeViewSet,
    FeedbackViewSet,
    MentorshipConnectionViewSet,
    CommunityDataViewSet,
    ReputationViewSet
)

router = DefaultRouter()
router.register(r'badges', BadgeViewSet, basename='badge')
router.register(r'user-badges', UserBadgeViewSet, basename='user-badge')
router.register(r'feedback', FeedbackViewSet, basename='feedback')
router.register(r'mentorships', MentorshipConnectionViewSet, basename='mentorship')
router.register(r'data', CommunityDataViewSet, basename='community-data')
router.register(r'reputation', ReputationViewSet, basename='reputation')

urlpatterns = [
    path('', include(router.urls)),
    # Leaderboard endpoint (dignity-first highlights, not rankings)
    path('leaderboard/', ReputationViewSet.as_view({'get': 'community_highlights'}), name='leaderboard'),
]

