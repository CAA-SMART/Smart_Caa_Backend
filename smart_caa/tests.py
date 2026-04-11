from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Attachment, EverydayCategory, History, Person, PatientPictogram, Pictogram


class AttachmentHistoryLinkTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='attachment-user', password='123456')
        self.client.force_authenticate(user=self.user)

        self.patient = Person.objects.create(
            name='Paciente Anexo',
            cpf='22345678901',
            email='paciente.anexo@example.com',
            phone='11999991111',
            is_patient=True,
        )
        self.caregiver = Person.objects.create(
            name='Cuidador Anexo',
            cpf='32345678901',
            email='cuidador.anexo@example.com',
            phone='11999992222',
            is_caregiver=True,
        )
        self.history = History.objects.create(
            patient=self.patient,
            caregiver=self.caregiver,
            description='Histórico clínico vinculado ao anexo.',
            created_by=self.user,
        )
        self.url = reverse('attachment-list-create')

    def _make_file(self, name='relatorio.pdf'):
        return SimpleUploadedFile(
            name,
            b'%PDF-1.4\n%teste de anexo\n',
            content_type='application/pdf',
        )

    def test_create_attachment_with_optional_history_link(self):
        response = self.client.post(
            self.url,
            {
                'name': 'Relatório Terapêutico',
                'patient': self.patient.id,
                'history': self.history.id,
                'file': self._make_file(),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Attachment.objects.count(), 1)

        attachment = Attachment.objects.get()
        self.assertEqual(attachment.patient, self.patient)
        self.assertEqual(attachment.history, self.history)
        self.assertEqual(response.data['history'], self.history.id)

    def test_create_attachment_without_history_still_works(self):
        response = self.client.post(
            self.url,
            {
                'name': 'Receita sem histórico',
                'patient': self.patient.id,
                'file': self._make_file('receita.pdf'),
            },
            format='multipart',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        attachment = Attachment.objects.get(name='Receita sem histórico')
        self.assertIsNone(getattr(attachment, 'history', None))

    def test_list_attachments_can_filter_by_history_id(self):
        other_history = History.objects.create(
            patient=self.patient,
            caregiver=self.caregiver,
            description='Outro histórico do paciente.',
            created_by=self.user,
        )

        Attachment.objects.create(
            name='Anexo filtrado',
            patient=self.patient,
            history=self.history,
            file=self._make_file('filtrado.pdf'),
            created_by=self.user,
        )
        Attachment.objects.create(
            name='Anexo de outro histórico',
            patient=self.patient,
            history=other_history,
            file=self._make_file('outro.pdf'),
            created_by=self.user,
        )

        response = self.client.get(self.url, {'history_id': self.history.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Anexo filtrado')
        self.assertEqual(response.data['results'][0]['history'], self.history.id)


class HistoryListAttachmentCountTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='history-user', password='123456')
        self.client.force_authenticate(user=self.user)

        self.patient = Person.objects.create(
            name='Paciente Histórico',
            cpf='42345678901',
            email='paciente.historico@example.com',
            phone='11999993333',
            is_patient=True,
        )
        self.caregiver = Person.objects.create(
            name='Cuidador Histórico',
            cpf='52345678901',
            email='cuidador.historico@example.com',
            phone='11999994444',
            is_caregiver=True,
        )
        self.history_with_attachments = History.objects.create(
            patient=self.patient,
            caregiver=self.caregiver,
            description='Histórico com anexos',
            created_by=self.user,
        )
        self.history_without_attachments = History.objects.create(
            patient=self.patient,
            caregiver=self.caregiver,
            description='Histórico sem anexos',
            created_by=self.user,
        )

        Attachment.objects.create(
            name='Exame 1',
            patient=self.patient,
            history=self.history_with_attachments,
            file=SimpleUploadedFile('exame1.pdf', b'pdf1', content_type='application/pdf'),
            created_by=self.user,
        )
        Attachment.objects.create(
            name='Exame 2',
            patient=self.patient,
            history=self.history_with_attachments,
            file=SimpleUploadedFile('exame2.pdf', b'pdf2', content_type='application/pdf'),
            created_by=self.user,
        )

        self.url = reverse('history-list-create')

    def test_list_patient_histories_returns_attachment_count_per_history(self):
        response = self.client.get(self.url, {'patient_id': self.patient.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)

        results_by_id = {item['id']: item for item in response.data['results']}

        self.assertEqual(results_by_id[self.history_with_attachments.id]['attachment_count'], 2)
        self.assertEqual(results_by_id[self.history_without_attachments.id]['attachment_count'], 0)


class PatientRegistrationOptionalFieldsTests(APITestCase):
    def setUp(self):
        self.url = reverse('patient-list-create')

    def test_create_patient_accepts_optional_birth_date_and_gender(self):
        payload = {
            'name': 'Paciente Cadastro',
            'cpf': '52998224725',
            'email': 'paciente.cadastro@example.com',
            'phone': '11999997777',
            'birth_date': '2018-05-10',
            'gender': 'Masculino',
            'password': 'SenhaForte@123'
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['birth_date'], payload['birth_date'])
        self.assertEqual(response.data['gender'], payload['gender'])


class AnamnesisSectionsStructureTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='anamnesis-user', password='123456')
        self.client.force_authenticate(user=self.user)

        self.patient = Person.objects.create(
            name='Paciente Anamnese',
            cpf='62345678901',
            email='paciente.anamnese@example.com',
            phone='11999995555',
            is_patient=True,
        )
        self.caregiver = Person.objects.create(
            name='Cuidadora Anamnese',
            cpf='72345678901',
            email='cuidadora.anamnese@example.com',
            phone='11999996666',
            is_caregiver=True,
        )
        self.url = reverse('patient-anamnesis-create', kwargs={'patient_id': self.patient.id})

    def test_create_anamnesis_with_sections_one_three_and_four(self):
        payload = {
            'caregiver': self.caregiver.id,
            'main_diagnosis': 'TEA',
            'associated_conditions': 'TDAH',
            'responsible_contact': 'Maria Silva - (11) 99999-0000',
            'reference_professional': 'Dra. Ana - Fonoaudióloga',
            'cognitive_level': 'Moderado',
            'attention_duration': '10-15 minutos',
            'memory_profile': 'Melhor memória visual',
            'learning_pace': 'Normal',
            'language_style': 'Literal',
            'auditory_comprehension': 'Compreende frases simples',
            'functional_speech': 'Sim, parcial',
            'speech_intelligibility': 'Pouco inteligível',
            'uses_gestures': True,
            'uses_signs': False,
            'uses_images_or_symbols': True,
            'preferred_symbol_systems': 'Arasaac, Fotografias',
            'symbol_comprehension': 'Muitos',
            'communication_priorities': 'Expressar necessidades, socializar'
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['reference_professional'], payload['reference_professional'])
        self.assertEqual(response.data['cognitive_level'], payload['cognitive_level'])
        self.assertEqual(response.data['functional_speech'], payload['functional_speech'])
        self.assertTrue(response.data['uses_gestures'])
        self.assertNotIn('expressive_vocabulary', response.data)
        self.assertNotIn('communication_methods', response.data)
        self.assertNotIn('general_observations', response.data)


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


class PatientPictogramDestroyViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='unlinker', password='123456')
        self.client.force_authenticate(user=self.user)

        self.patient = Person.objects.create(
            name='Paciente Desvinculação',
            cpf='12345678903',
            email='paciente.desvinculacao@example.com',
            phone='11999990002',
            is_patient=True,
        )
        self.category = EverydayCategory.objects.create(
            name='Ações',
            created_by=self.user,
        )
        self.url = reverse('patient-pictogram-destroy', kwargs={'patient_id': self.patient.id})

    def _make_image(self, name='unlink.gif'):
        return SimpleUploadedFile(
            name,
            (
                b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00'
                b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00'
                b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
            ),
            content_type='image/gif',
        )

    def _create_linked_pictogram(self, name):
        pictogram = Pictogram.objects.create(
            name=name,
            category=self.category,
            image=self._make_image(f'{name}.gif'),
            private=False,
            created_by=self.user,
        )
        link = PatientPictogram.objects.create(
            patient=self.patient,
            pictogram=pictogram,
            created_by=self.user,
        )
        return pictogram, link

    def test_destroy_inactivates_links_instead_of_deleting_rows(self):
        first_pictogram, first_link = self._create_linked_pictogram('Comer')
        second_pictogram, second_link = self._create_linked_pictogram('Beber')

        response = self.client.post(
            self.url,
            {'pictograms': [first_pictogram.id, second_pictogram.id]},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        first_link.refresh_from_db()
        second_link.refresh_from_db()

        self.assertFalse(first_link.is_active)
        self.assertFalse(second_link.is_active)
        self.assertEqual(first_link.inactivated_by, self.user)
        self.assertEqual(second_link.inactivated_by, self.user)
        self.assertIsNotNone(first_link.inactivated_at)
        self.assertIsNotNone(second_link.inactivated_at)
        self.assertEqual(
            PatientPictogram.objects.filter(
                patient=self.patient,
                pictogram__in=[first_pictogram, second_pictogram],
            ).count(),
            2,
        )
        self.assertEqual(response.data['message'], '2 pictogramas desvinculados com sucesso.')

    def test_destroy_endpoint_also_accepts_single_pictogram_payload(self):
        pictogram, link = self._create_linked_pictogram('Banheiro')

        response = self.client.post(
            self.url,
            {'pictogram': pictogram.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Pictograma desvinculado com sucesso.')

        link.refresh_from_db()
        self.assertFalse(link.is_active)
        self.assertEqual(link.inactivated_by, self.user)

    def test_destroy_is_atomic_when_any_pictogram_is_not_linked(self):
        linked_pictogram, linked = self._create_linked_pictogram('Escovar')
        unlinked_pictogram = Pictogram.objects.create(
            name='Dormir',
            category=self.category,
            image=self._make_image('Dormir.gif'),
            private=False,
            created_by=self.user,
        )

        response = self.client.post(
            self.url,
            {'pictograms': [linked_pictogram.id, unlinked_pictogram.id]},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        linked.refresh_from_db()
        self.assertTrue(linked.is_active)
        self.assertIsNone(linked.inactivated_at)


class PatientPictogramReactivationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reactivator', password='123456')
        self.client.force_authenticate(user=self.user)

        self.patient = Person.objects.create(
            name='Paciente Reativação',
            cpf='12345678904',
            email='paciente.reativacao@example.com',
            phone='11999990003',
            is_patient=True,
        )
        self.category = EverydayCategory.objects.create(
            name='Reativação',
            created_by=self.user,
        )
        self.create_url = reverse('patient-pictogram-create', kwargs={'patient_id': self.patient.id})
        self.destroy_url = reverse('patient-pictogram-destroy', kwargs={'patient_id': self.patient.id})

    def _make_image(self, name='reactivate.gif'):
        return SimpleUploadedFile(
            name,
            (
                b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00'
                b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00'
                b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
            ),
            content_type='image/gif',
        )

    def _create_linked_pictogram(self, name):
        pictogram = Pictogram.objects.create(
            name=name,
            category=self.category,
            image=self._make_image(f'{name}.gif'),
            private=False,
            created_by=self.user,
        )
        link = PatientPictogram.objects.create(
            patient=self.patient,
            pictogram=pictogram,
            created_by=self.user,
        )
        return pictogram, link

    def test_create_reactivates_existing_inactive_link_instead_of_creating_new_one(self):
        pictogram, link = self._create_linked_pictogram('Lavar as mãos')

        destroy_response = self.client.post(
            self.destroy_url,
            {'pictogram': pictogram.id},
            format='json',
        )
        self.assertEqual(destroy_response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            self.create_url,
            {'pictogram': pictogram.id},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        link.refresh_from_db()
        self.assertTrue(link.is_active)
        self.assertIsNone(link.inactivated_at)
        self.assertIsNone(link.inactivated_by)
        self.assertEqual(
            PatientPictogram.objects.filter(patient=self.patient, pictogram=pictogram).count(),
            1,
        )
        self.assertEqual(response.data['data']['id'], link.id)

    def test_batch_create_reactivates_existing_inactive_links(self):
        first_pictogram, first_link = self._create_linked_pictogram('Pegar')
        second_pictogram, second_link = self._create_linked_pictogram('Guardar')

        destroy_response = self.client.post(
            self.destroy_url,
            {'pictograms': [first_pictogram.id, second_pictogram.id]},
            format='json',
        )
        self.assertEqual(destroy_response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            self.create_url,
            {'pictograms': [first_pictogram.id, second_pictogram.id]},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        first_link.refresh_from_db()
        second_link.refresh_from_db()

        self.assertTrue(first_link.is_active)
        self.assertTrue(second_link.is_active)
        self.assertEqual(
            PatientPictogram.objects.filter(
                patient=self.patient,
                pictogram__in=[first_pictogram, second_pictogram],
            ).count(),
            2,
        )
