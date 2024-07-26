from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.exceptions import ObjectDoesNotExist
from .models import Subject, Mark, Event, Attendance, TimetableClass,UserSubjectLink,CustomUser ,Exam,Student,Classes
from .serializers import UserSerializer, SubjectSerializer, MarkSerializer, EventSerializer, AttendanceSerializer, TimetableSerializer, LoginSerializer, SignupSerializer,UserSubjectSerializer,ExamSerializer,StudentSerializer,ClasseSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAdminUser
from .permissions import IsTeacher, IsAdmin, IsStudent,TeacherCreateStudentViewOnly

class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class LoginViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    queryset = CustomUser.objects.none()

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username': user.username
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class StudentBioViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        try:
            user = CustomUser.objects.get(id=request.user.id)
            print(user)
            
            try:
                student = Student.objects.get(user=user)
                serializer2 = StudentSerializer(student)
                
                markquery = Mark.objects.filter(student=user)
                print(markquery)
                sheet = []
                
                if markquery.exists():
                    serializer_mark = MarkSerializer(markquery, many=True)
                    for obj in serializer_mark.data:
                        marks = {}
                        print("-----",obj.get('exam'))
                        examname = Exam.objects.get(id=obj.get('exam')).exam_type
                        subname = Exam.objects.get(id=obj.get('exam')).subject.subname
                        marks['subject'] = subname
                        marks['exam'] = examname
                        
                        marks['marks_obtained'] = obj.get('marks_obtained')
                        sheet.append(marks)
                else:
                    print("No marks found for this student")
                
                serializer1 = UserSerializer(user)
                merged_bio = {**serializer1.data, **serializer2.data}
                merged_bio['results'] = sheet
                
                
                return Response(merged_bio)
            
            except ObjectDoesNotExist:
                return Response({"error": "No Student profile found for this user"}, status=status.HTTP_404_NOT_FOUND)
        
        except ObjectDoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        request.data["user"]=CustomUser.objects.get(username=request.data["user"]).id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            
class SignupViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer
    queryset = CustomUser.objects.none()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                
                'message': 'User created successfully',
                'username': user.username,
                'role': user.role
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def list(self, request):

        queryset = CustomUser.objects.get(email=request.user.email)
        serializer = UserSerializer(queryset)
        return Response(serializer.data)
    

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsTeacher]
    
    

class AddSubjectViewSet(viewsets.ModelViewSet):
    
    serializer_class = UserSubjectSerializer


    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Usersubjectlink.objects.filter(user=request.user)
        serializer = UserSubjectSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        userid=request.user.id
        request.data['user']=userid
        request.data['subject']=Subject.objects.get(subname=request.data['subject']).id
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

    

    
    

class MarkViewSet(viewsets.ModelViewSet):
    queryset = Mark.objects.all()
    serializer_class = MarkSerializer
    permission_classes = [TeacherCreateStudentViewOnly]

    def create(self, request):
        request.data['student'] = CustomUser.objects.get(username=request.data['student']).id
        request.data['subject'] = Subject.objects.get(subname=request.data['subject']).id
        request.data['exam'] = Exam.objects.get(exam_type=request.data['exam']).id
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list (self,request):
        queryset = Mark.objects.all()
        
        serializer = MarkSerializer(queryset, many=True)
        
        
        for obj in serializer.data:
            studname=CustomUser.objects.get(id=obj.get('student')).username
            examname=Exam.objects.get(id=obj.get('exam')).exam_type
            obj['student']=studname
            obj['exam']=examname
            
        
        
        return Response(serializer.data)





class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [TeacherCreateStudentViewOnly]

    def create(self, request):
        # print(request.data['event_in_charge'])
        request.data['event_in_charge'] = CustomUser.objects.get(username=request.data['event_in_charge']).id
        request.data['security_in_charge'] = CustomUser.objects.get(username=request.data['security_in_charge']).id
        request.data['room'] = Classes.objects.get(class_name=request.data['room']).id
        print("--------------------------------------",request.data['event_in_charge'])
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def list (self, request):
        queryset = Event.objects.all()
        serializer = EventSerializer(queryset, many=True)
        for obj in serializer.data:
            event_in_charge=CustomUser.objects.get(id=obj.get('event_in_charge')).username
            security_in_charge=CustomUser.objects.get(id=obj.get('security_in_charge')).username
            room=Classes.objects.get(id=obj.get('room')).class_name
            obj['room']=room
            obj['security_in_charge']=security_in_charge
            obj['event_in_charge']=event_in_charge
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [TeacherCreateStudentViewOnly]

    def create(self, request):
        request.data['student'] = CustomUser.objects.get(username=request.data['student']).id
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list (self,request):
        print(request.user)
        queryset = Attendance.objects.filter(student=request.user)

        serializer = AttendanceSerializer(queryset, many=True)
        
        for obj in serializer.data:
            studname=CustomUser.objects.get(id=obj.get('student')).username
            
            obj['student']=studname
            
        
        
        return Response(serializer.data)

class TimetableViewSet(viewsets.ModelViewSet):
    queryset = TimetableClass.objects.all()
    serializer_class = TimetableSerializer
    permission_classes = [TeacherCreateStudentViewOnly]

    def create(self, request):
        request.data['teacher'] = CustomUser.objects.get(username=request.data['teacher']).id
        request.data['room'] = Classes.objects.get(class_name=request.data['room']).id
        
        
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list (self,request):
        queryset = TimetableClass.objects.all()

        serializer = TimetableSerializer(queryset, many=True)
        
        for obj in serializer.data:
            teachername=CustomUser.objects.get(id=obj.get('teacher')).username
            roomname=Classes.objects.get(id=obj.get('room')).class_name
            obj['room']=roomname
            
            obj['teacher']=teachername
            
        
        
        return Response(serializer.data)


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [TeacherCreateStudentViewOnly]

    def create(self, request):
        request.data['subject'] = Subject.objects.get(subname=request.data['subject']).id
        request.data['classnumber'] = Classes.objects.get(class_name=request.data['classnumber']).id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list (self,request):
        queryset = Exam.objects.all()

        serializer = ExamSerializer(queryset, many=True)
        
        for obj in serializer.data:
            subname=Subject.objects.get(id=obj.get('subject')).subname
            
            obj['subject']=subname
            
        
        
        return Response(serializer.data)

class ClasseViewSet(viewsets.ModelViewSet):
    queryset = Classes.objects.all()
    serializer_class = ClasseSerializer
    permission_classes = [TeacherCreateStudentViewOnly]

    def create(self, request):
        request.data['class_teacher'] = CustomUser.objects.get(username=request.data['class_teacher']).id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list (self,request):
        queryset = Classes.objects.all()

        serializer = ClasseSerializer(queryset, many=True)
        
        for obj in serializer.data:
            class_teacher=CustomUser.objects.get(id=obj.get('class_teacher')).username
            
            obj['class_teacher']=class_teacher
            
        
        
        return Response(serializer.data)

