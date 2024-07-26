from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Subject, Mark, Event, Attendance, TimetableClass,UserSubjectLink,CustomUser,Exam,Student,Classes

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']

class SignupSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLES)
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password','role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data['role'],
        )
        
        return user

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['user', 'roll_no', 'admission_number', 'address', 'dob', 'father_name', 'classnumber']

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'subname', 'description']

class UserSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubjectLink
        fields = ['id', 'user', 'subject']


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mark
        fields = ['id', 'student', 'exam', 'marks_obtained']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'date', 'room', 'security_in_charge', 'event_in_charge']

class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'date', 'present']

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableClass
        fields = ['id', 'class_type', 'teacher', 'room', 'date', 'time']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            return data
        raise serializers.ValidationError("Must include 'username' and 'password'.")

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = ['id', 'exam_type', 'date', 'classnumber',"time","subject"]

class ClasseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classes
        fields =  ['id','class_name','class_teacher']
        
    
