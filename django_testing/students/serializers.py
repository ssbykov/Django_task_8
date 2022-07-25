from rest_framework import serializers

from students.models import Course
from django_testing import settings


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ("id", "name", "students")

    def validate_students(self, students):
        if len(students) > settings.MAX_STUDENTS_PER_COURSE:
            raise serializers.ValidationError('Превышено максимальное количество студентов на курсе')

        return students
