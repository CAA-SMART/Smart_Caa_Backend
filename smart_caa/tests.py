from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import EverydayCategory, Person, PatientPictogram, Pictogram


class PatientCustomPictogramCreateViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='123456')
        self.client.force_authenticate(user=self.user)

        self.patient = Person.objects.create(
            name='Paciente Teste',
            cpf='12345678901',
            email='paciente@example.com',
            phone='11999990000',
            is_patient=True,
        )
        self.category = EverydayCategory.objects.create(
            name='Rotina',
            created_by=self.user,
        )
        self.url = reverse('patient-custom-pictogram-create', kwargs={'patient_id': self.patient.id})

    def _make_image(self, name='pictogram.gif'):
        return SimpleUploadedFile(
            name,
            (
                b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00'
                b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00'
                b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
            ),
            content_type='image/gif',
        )

    def test_create_custom_pictogram_and_link_to_patient(self):
        response = self.client.post(
            self.url,
            {
                'name': 'Água',
                'category': self.category.id,
                'description': 'Pictograma personalizado de água',
                'image': self._make_image(),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Pictogram.objects.count(), 1)
        self.assertEqual(PatientPictogram.objects.count(), 1)

        pictogram = Pictogram.objects.get()
        link = PatientPictogram.objects.get()

        self.assertTrue(pictogram.private)
        self.assertFalse(pictogram.is_default)
        self.assertEqual(pictogram.created_by, self.user)
        self.assertEqual(link.patient, self.patient)
        self.assertEqual(link.pictogram, pictogram)
        self.assertEqual(link.created_by, self.user)
        self.assertEqual(response.data['data']['pictogram'], pictogram.id)
        self.assertEqual(response.data['data']['pictogram_name'], 'Água')

    def test_does_not_create_pictogram_when_patient_is_invalid(self):
        non_patient = Person.objects.create(
            name='Pessoa Sem Perfil de Paciente',
            cpf='12345678902',
            email='nao-paciente@example.com',
            phone='11999990001',
            is_caregiver=True,
        )
        url = reverse('patient-custom-pictogram-create', kwargs={'patient_id': non_patient.id})

        response = self.client.post(
            url,
            {
                'name': 'Banho',
                'category': self.category.id,
                'description': 'Não deve persistir no banco',
                'image': self._make_image('banho.gif'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Pictogram.objects.count(), 0)
        self.assertEqual(PatientPictogram.objects.count(), 0)

    def test_list_patient_pictograms_can_filter_by_private_flag(self):
        private_pictogram = Pictogram.objects.create(
            name='Privado',
            category=self.category,
            image=self._make_image('privado.gif'),
            private=True,
            created_by=self.user,
        )
        public_pictogram = Pictogram.objects.create(
            name='Publico',
            category=self.category,
            image=self._make_image('publico.gif'),
            private=False,
            created_by=self.user,
        )
        PatientPictogram.objects.create(
            patient=self.patient,
            pictogram=private_pictogram,
            created_by=self.user,
        )
        PatientPictogram.objects.create(
            patient=self.patient,
            pictogram=public_pictogram,
            created_by=self.user,
        )

        list_url = reverse('patient-pictograms-list', kwargs={'patient_id': self.patient.id})

        private_response = self.client.get(list_url, {'private': 'true'})
        public_response = self.client.get(list_url, {'private': 'false'})

        self.assertEqual(private_response.status_code, status.HTTP_200_OK)
        self.assertEqual(public_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(private_response.data), 1)
        self.assertEqual(len(public_response.data), 1)
        self.assertEqual(private_response.data[0]['pictogram_name'], 'Privado')
        self.assertEqual(public_response.data[0]['pictogram_name'], 'Publico')
