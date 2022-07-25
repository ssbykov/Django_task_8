import pytest

from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Student, Course

class TestCourses():
    URL = '/api/v1/courses/'
    name = 'Новый курс'
    date = {'name': name}

    def __int__(self):
        self.courses = []

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def student_factory(self):
        def factory(*args, **kwargs):
            return baker.make(Student, *args, **kwargs)

        return factory

    @pytest.fixture
    def course_factory(self):
        def factory(*args, **kwargs):
            return baker.make(Course, *args, **kwargs)

        return factory

    @pytest.fixture
    @pytest.mark.django_db
    def corse_data(self, client, course_factory, student_factory):
        students = student_factory(_quantity=4)
        self.courses = course_factory(_quantity=5, students=students)
        return self.courses


    # проверка выдачи данных по одному курсу
    @pytest.mark.django_db
    def test_get_courses_retrieve(self, client, corse_data):
        for i in range(len(self.courses)):
            response = client.get(f'{self.URL}{i + 1}/')
            assert response.status_code == 200
            data = response.json()
            assert data.get('name') == self.courses[i].name
            assert len(data.get('students')) == self.courses[i].students.all().count()

    # проверка выдачи данных по списку курсов
    @pytest.mark.django_db
    def test_get_courses(self, client, corse_data):
        response = client.get(self.URL)
        assert response.status_code == 200
        data = response.json()
        for i, m in enumerate(data):
            assert m.get('name') == self.courses[i].name
            assert len(m.get('students')) == self.courses[i].students.all().count()

    # проверка фильтрации курсов по id
    @pytest.mark.django_db
    def test_get_courses_filter_id(self, client, corse_data):
        for course in self.courses:
            response = client.get(f'{self.URL}?id={course.id}')
            assert response.status_code == 200
            data = response.json()
            assert data[0].get('name') == course.name
            assert len(data[0].get('students')) == course.students.all().count()

    # проверка фильтрации курсов по name
    @pytest.mark.django_db
    def test_get_courses_filter_name(self, client, corse_data):
        for course in self.courses:
            response = client.get(f'/api/v1/courses/?name={course.name}')
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert len(data[0].get('students')) == course.students.all().count()

    # проверка создания курса без названия
    @pytest.mark.django_db
    def test_post_course_without_name_400(self, client):
        response = client.post(self.URL)
        assert response.status_code == 400

    # проверка создания курса
    @pytest.mark.django_db
    def test_post_course_201(self, client):
        response = client.post(self.URL, data=self.date)
        assert response.status_code == 201
        assert response.data.get('name') == self.name

    # проверка изменения курса без названия
    @pytest.mark.django_db
    def test_patch_course_without_name_400(self, client, corse_data):
        response = client.patch(f'{self.URL}{self.courses[0].id}/', data={'name': ''})
        assert response.status_code == 400

    # проверка изменения курса
    @pytest.mark.django_db
    def test_patch_course_name_200(self, client, corse_data):
        response = client.patch(f'{self.URL}{self.courses[0].id}/', data=self.date)
        assert response.status_code == 200
        assert response.data.get('name') == self.name

    # проверка удаления курса
    @pytest.mark.django_db
    def test_delete_course(self, client, corse_data):
        response = client.delete(f'{self.URL}{self.courses[0].id}/')
        assert response.status_code == 204
        assert response.data == None

    #дополнительное задание
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        ["students", "expected_status"],
        (
                (3, status.HTTP_201_CREATED),
                (25, status.HTTP_400_BAD_REQUEST),
                (0, status.HTTP_201_CREATED)
        )
    )
    def test_post_course_settings(self, client, student_factory, settings, students, expected_status):
        settings.MAX_STUDENTS_PER_COURSE = 2
        students = student_factory(_quantity=30)[:students]
        students = {'students': [i.id for i in students]}
        response = client.post(self.URL, data=self.date | students)
        assert response.status_code == expected_status
