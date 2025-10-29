from django.urls import path
from . import views

app_name = "maths"
urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("dashboard/", views.dashboard_detail, name="dashboard_detail"),
    path("topics/", views.topic_list, name="topics"),
    path("topic/<int:topic_id>/levels/", views.level_list, name="levels"),
    path("level/<int:level_number>/", views.level_detail, name="level_detail"),
    path("create-class/", views.create_class, name="create_class"),
    path("join-class/", views.join_class, name="join_class"),
    path("signup/student/", views.signup_student, name="signup_student"),
    path("signup/teacher/", views.signup_teacher, name="signup_teacher"),
    path("register/teacher-center/", views.teacher_center_registration, name="teacher_center_registration"),
    path("register/individual-student/", views.individual_student_registration, name="individual_student_registration"),
    path("bulk-student-registration/", views.bulk_student_registration, name="bulk_student_registration"),
    path("level/<int:level_number>/questions/", views.level_questions, name="level_questions"),
    path("level/<int:level_number>/add-question/", views.add_question, name="add_question"),
    path("level/<int:level_number>/quiz/", views.take_quiz, name="take_quiz"),
    path("level/<int:level_number>/practice/", views.practice_questions, name="practice_questions"),
    path("level/<int:level_number>/measurements/", views.measurements_questions, name="measurements_questions"),
    path("level/<int:level_number>/measurements-progress/", views.measurements_progress, name="measurements_progress"),
]
