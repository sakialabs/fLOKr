from django.urls import path
from .views import (
    ImageTagView,
    RecommendationsView,
    SeasonalRecommendationsView,
    ComplementaryItemsView,
    NewcomerEssentialsView,
    PopularItemsView,
    AskQuestionView,
    PopularFAQsView,
    FAQsByCategoryView
)

app_name = 'ori_ai'

urlpatterns = [
    # Image tagging
    path('image-tag/', ImageTagView.as_view(), name='image-tag'),
    
    # Recommendations
    path('recommendations/', RecommendationsView.as_view(), name='recommendations'),
    path('recommendations/seasonal/', SeasonalRecommendationsView.as_view(), name='seasonal-recommendations'),
    path('recommendations/complementary/', ComplementaryItemsView.as_view(), name='complementary-items'),
    path('recommendations/newcomer-essentials/', NewcomerEssentialsView.as_view(), name='newcomer-essentials'),
    path('recommendations/popular/', PopularItemsView.as_view(), name='popular-items'),
    
    # Q&A System
    path('ask/', AskQuestionView.as_view(), name='ask-question'),
    path('faqs/popular/', PopularFAQsView.as_view(), name='popular-faqs'),
    path('faqs/category/', FAQsByCategoryView.as_view(), name='faqs-by-category'),
]
