from django.contrib.auth.models import User
from django.test import TestCase

from .models import (ProgramBlock, Sport, Training, TrainingBlock,
                     TrainingProgram, TrainingRecord, UserProfile)


class PortalTestCase(TestCase):

    def setUp(self):
        self.sport = Sport.objects.create(name='Футбол', description='Секция футбола')
        self.training = Training.objects.create(
            sport=self.sport, type='section', day='mon',
            time_start='18:00', time_end='19:30', location='Стадион МУИВ', capacity=2)

        self.student = self.make_user('student', 'student')
        self.coach = self.make_user('coach', 'coach')

    def make_user(self, username, role):
        user = User.objects.create_user(username, password='pass12345')
        UserProfile.objects.create(user=user, role=role)
        return user


class TrainingRegisterTests(PortalTestCase):

    def test_student_can_register(self):
        """Студент записывается на тренировку."""
        self.client.force_login(self.student)
        self.client.get(f'/schedule/register/{self.training.pk}/')
        self.assertEqual(TrainingRecord.objects.filter(training=self.training).count(), 1)

    def test_capacity_is_limited(self):
        """Запись сверх количества мест не проходит."""

        for name in ('ivanov', 'petrov'):
            self.client.force_login(self.make_user(name, 'student'))
            self.client.get(f'/schedule/register/{self.training.pk}/')

        self.client.force_login(self.student)
        self.client.get(f'/schedule/register/{self.training.pk}/')
        self.assertEqual(TrainingRecord.objects.filter(training=self.training).count(), 2)


class AccessTests(PortalTestCase):

    def test_student_has_no_access_to_coach_pages(self):
        """Студент не допускается в кабинет тренера."""
        self.client.force_login(self.student)
        response = self.client.get('/profile/coach/blocks/')
        self.assertRedirects(response, '/profile/')

    def test_coach_has_access_to_blocks(self):
        """Тренер открывает библиотеку блоков."""
        self.client.force_login(self.coach)
        self.assertEqual(self.client.get('/profile/coach/blocks/').status_code, 200)


class BlockTests(PortalTestCase):

    def test_coach_creates_block(self):
        """Тренер создаёт блок занятия."""
        self.client.force_login(self.coach)
        self.client.post('/profile/coach/blocks/add/', {
            'title': 'Ведение мяча между стойками',
            'sport': self.sport.pk,
            'kind': 'main',
            'duration_min': 10,
            'equipment': '5 стоек, мяч',
            'description': 'Игрок ведёт мяч змейкой, обходя стойки.',
            'scheme': '',
        })
        self.assertTrue(TrainingBlock.objects.filter(title='Ведение мяча между стойками').exists())


class ProgramTests(PortalTestCase):

    def setUp(self):
        super().setUp()
        self.program = TrainingProgram.objects.create(
            title='Футбол с нуля', sport=self.sport,
            description='Курс для студентов без опыта игры.')
        self.block = TrainingBlock.objects.create(
            title='Разминка в движении', sport=self.sport, kind='warmup',
            duration_min=10, description='Бег по периметру площадки.')

    def test_coach_adds_block_to_program(self):
        """Тренер добавляет блок в программу."""
        self.client.force_login(self.coach)
        self.client.post(f'/profile/coach/programs/{self.program.pk}/', {
            'block': self.block.pk, 'session': 1, 'order': 1,
        })
        self.assertEqual(self.program.items.count(), 1)

    def test_program_exports_to_pdf(self):
        """Программа выгружается в формате PDF."""
        ProgramBlock.objects.create(
            program=self.program, block=self.block, session=1, order=1)
        response = self.client.get(f'/programs/{self.program.pk}/pdf/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertTrue(response.content.startswith(b'%PDF'))


class ReportTests(PortalTestCase):

    def test_coach_exports_attendance(self):
        """Отчёт по посещаемости выгружается в Excel."""
        TrainingRecord.objects.create(user=self.student, training=self.training, attended=True)
        self.client.force_login(self.coach)
        response = self.client.get('/profile/coach/export/xlsx/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheetml', response['Content-Type'])