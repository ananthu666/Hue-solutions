from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LoginViewSet, SignupViewSet, UserViewSet, SubjectViewSet, MarkViewSet, EventViewSet, AttendanceViewSet, TimetableViewSet,AddSubjectViewSet,ExamViewSet,StudentBioViewSet,ClasseViewSet

router = DefaultRouter()
router.register(r'signup', SignupViewSet, basename='signup')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'student_bio', StudentBioViewSet, basename='student_bio')
router.register(r'users', UserViewSet, basename='users')
router.register(r'subjects', SubjectViewSet, basename='subjects')
router.register(r'add_subject', AddSubjectViewSet, basename='add_subject')
router.register(r'marks', MarkViewSet, basename='marks')
router.register(r'events', EventViewSet, basename='events')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'timetable', TimetableViewSet, basename='timetable')
router.register(r'exam', ExamViewSet, basename='exam')
router.register(r'classes', ClasseViewSet, basename='classes')


urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]