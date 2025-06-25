from django.urls import path
from .views import (
    EverydayCategoryCreateListView, 
    EverydayCategoryRetrieveUpdateDestroyView,
    PictogramCreateListView,
    PictogramRetrieveUpdateDestroyView,
    PatientCreateListView,
    PatientRetrieveUpdateDestroyView,
    CaregiverCreateListView,
    CaregiverRetrieveUpdateDestroyView
)

urlpatterns = [
    # EverydayCategory endpoints
    path('api/everyday-categories/', EverydayCategoryCreateListView.as_view(), name='everyday-category-list-create'),
    path('api/everyday-categories/<int:pk>/', EverydayCategoryRetrieveUpdateDestroyView.as_view(), name='everyday-category-detail'),
    
    # Pictogram endpoints
    path('api/pictograms/', PictogramCreateListView.as_view(), name='pictogram-list-create'),
    path('api/pictograms/<int:pk>/', PictogramRetrieveUpdateDestroyView.as_view(), name='pictogram-detail'),
    
    # Patient endpoints
    path('api/patients/', PatientCreateListView.as_view(), name='patient-list-create'),
    path('api/patients/<int:pk>/', PatientRetrieveUpdateDestroyView.as_view(), name='patient-detail'),
    
    # Caregiver endpoints
    path('api/caregivers/', CaregiverCreateListView.as_view(), name='caregiver-list-create'),
    path('api/caregivers/<int:pk>/', CaregiverRetrieveUpdateDestroyView.as_view(), name='caregiver-detail'),
]
