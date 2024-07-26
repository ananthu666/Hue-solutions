from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLES, default='student')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    roll_no = models.IntegerField()
    admission_number = models.IntegerField()
    address = models.CharField(max_length=100)
    dob = models.DateField()
    father_name = models.CharField(max_length=50)
    classnumber = models.ForeignKey('Classes', on_delete=models.CASCADE, related_name='students')

    def __str__(self):
        return self.user.username

class Subject(models.Model):
    subname = models.CharField(max_length=50)
    description = models.TextField(max_length=200, default='No description available')

    def __str__(self):
        return self.subname

class UserSubjectLink(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='users')

    def __str__(self):
        return f"{self.user.username} - {self.subject.subname}"

class Mark(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='marks')
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='marks')
    marks_obtained = models.IntegerField()

    def __str__(self):
        return f"{self.student.username} - {self.exam.exam_type}: {self.marks_obtained}"

class Event(models.Model):
    name = models.CharField(max_length=50)
    date = models.DateField()
    room = models.ForeignKey('Classes', on_delete=models.CASCADE, related_name='events')
    security_in_charge = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='security_events')
    event_in_charge = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='event_events')

    def __str__(self):
        return self.name

class Attendance(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    present = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.username} - {self.date}: {'Present' if self.present else 'Absent'}"

class TimetableClass(models.Model):
    class_type = models.CharField(max_length=50)
    
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='timetables')
    room = models.ForeignKey('Classes', on_delete=models.CASCADE, related_name='timetables_room')
    date = models.DateField()
    time = models.TimeField()

    def __str__(self):
        return f"{self.class_type} - {self.teacher.username} ({self.date} {self.time})"

class Exam(models.Model):
    exam_type = models.CharField(max_length=50)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='exams')
    date = models.DateField()
    time = models.TimeField()
    classnumber = models.ForeignKey('Classes', on_delete=models.CASCADE, related_name='exams')

    def __str__(self):
        return self.exam_type

class Classes(models.Model):
    class_name = models.CharField(max_length=50)
    class_teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='classes')

    def __str__(self):
        return f"{self.class_name} - {self.class_teacher.username} (Teacher)"
    
    def save(self, *args, **kwargs):
        if self.class_teacher.role != 'teacher':
            raise ValueError("The assigned class teacher must have the role 'teacher'.")
        super().save(*args, **kwargs)

