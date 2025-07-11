from django.urls import path
from .views import (
    EverydayCategoryCreateListView, 
    EverydayCategoryRetrieveUpdateDestroyView,
    PictogramCreateListView,
    PictogramRetrieveUpdateDestroyView,
    PatientCreateListView,
    PatientRetrieveUpdateDestroyView,
    PatientCaregiversListView,
    PatientCaregiverCreateView,
    PatientCaregiverDetailView,
    PatientPictogramsListView,
    PatientPictogramCreateView,
    PatientPictogramDestroyView,
    PatientAvailablePictogramsView,
    CaregiverCreateListView,
    CaregiverRetrieveUpdateDestroyView,
    CaregiverPatientsListView,
    PatientCaregiverRelationshipListCreateView,
    PatientCaregiverRelationshipDetailView,
    PatientCaregiverRelationshipInactivateView,
    GetPersonByUserIdView,
    GetPersonByCpfView
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
    
    # Patient-Caregiver relationship endpoints (specific to patient)
    path('api/patients/<int:patient_id>/caregivers/', PatientCaregiversListView.as_view(), name='patient-caregivers-list'),
    path('api/patients/<int:patient_id>/caregivers/create/', PatientCaregiverCreateView.as_view(), name='patient-caregiver-create'),
    path('api/patients/<int:patient_id>/caregivers/<int:pk>/', PatientCaregiverDetailView.as_view(), name='patient-caregiver-detail'),
    
    # Patient-Pictogram relationship endpoints (specific to patient)
    path('api/patients/<int:patient_id>/pictograms/', PatientPictogramsListView.as_view(), name='patient-pictograms-list'),
    path('api/patients/<int:patient_id>/pictograms/create/', PatientPictogramCreateView.as_view(), name='patient-pictogram-create'),
    path('api/patients/<int:patient_id>/pictograms/<int:pk>/destroy/', PatientPictogramDestroyView.as_view(), name='patient-pictogram-destroy'),
    path('api/patients/<int:patient_id>/pictograms/available/', PatientAvailablePictogramsView.as_view(), name='patient-available-pictograms'),
    
    # Caregiver endpoints
    path('api/caregivers/', CaregiverCreateListView.as_view(), name='caregiver-list-create'),
    path('api/caregivers/<int:pk>/', CaregiverRetrieveUpdateDestroyView.as_view(), name='caregiver-detail'),
    
    # Caregiver-Patient relationship endpoints (specific to caregiver)
    path('api/caregivers/<int:caregiver_id>/patients/', CaregiverPatientsListView.as_view(), name='caregiver-patients-list'),
    
    # General Patient-Caregiver relationship endpoints
    path('api/relationships/', PatientCaregiverRelationshipListCreateView.as_view(), name='relationship-list-create'),
    path('api/relationships/<int:pk>/', PatientCaregiverRelationshipDetailView.as_view(), name='relationship-detail'),
    path('api/relationships/<int:pk>/inactivate/', PatientCaregiverRelationshipInactivateView.as_view(), name='relationship-inactivate'),
    
    # Person endpoints
    path('api/user/<int:user_id>/person/', GetPersonByUserIdView.as_view(), name='get-person-by-user-id'),
    path('api/person/cpf/<str:cpf>/', GetPersonByCpfView.as_view(), name='get-person-by-cpf'),
]
