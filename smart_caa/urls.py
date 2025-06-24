from django.urls import path
from .views import EverydayCategoryCreateListView, EverydayCategoryRetrieveUpdateDestroyView

urlpatterns = [
    path('api/everyday-categories/', EverydayCategoryCreateListView.as_view(), name='everyday-category-list-create'),
    path('api/everyday-categories/<int:pk>/', EverydayCategoryRetrieveUpdateDestroyView.as_view(), name='everyday-category-detail'),
]
