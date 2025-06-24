from django.urls import path
from .views import (
    EverydayCategoryCreateListView, 
    EverydayCategoryRetrieveUpdateDestroyView,
    PictogramCreateListView,
    PictogramRetrieveUpdateDestroyView
)

urlpatterns = [
    # EverydayCategory endpoints
    path('api/everyday-categories/', EverydayCategoryCreateListView.as_view(), name='everyday-category-list-create'),
    path('api/everyday-categories/<int:pk>/', EverydayCategoryRetrieveUpdateDestroyView.as_view(), name='everyday-category-detail'),
    
    # Pictogram endpoints
    path('api/pictograms/', PictogramCreateListView.as_view(), name='pictogram-list-create'),
    path('api/pictograms/<int:pk>/', PictogramRetrieveUpdateDestroyView.as_view(), name='pictogram-detail'),
]
