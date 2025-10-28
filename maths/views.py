from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
import time
from django.db.models import Q
import random
from .models import Topic, Level, ClassRoom, Enrollment, CustomUser, Question, Answer, StudentAnswer
from .forms import CreateClassForm, StudentSignUpForm, TeacherSignUpForm, TeacherCenterRegistrationForm, IndividualStudentRegistrationForm, StudentBulkRegistrationForm, QuestionForm, AnswerFormSet

def signup_student(request):
    if request.method == "POST":
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("maths:dashboard")
    else:
        form = StudentSignUpForm()
    return render(request, "maths/signup.html", {"form": form, "type": "Student"})

def signup_teacher(request):
    if request.method == "POST":
        form = TeacherSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("maths:dashboard")
    else:
        form = TeacherSignUpForm()
    return render(request, "maths/signup.html", {"form": form, "type": "Teacher"})

def student_allowed_levels(user):
    """
    Determine which levels a student can access.
    Returns None if user is a teacher or if individual student should see all levels.
    Returns a queryset of allowed levels if student is enrolled in classes.
    """
    if user.is_teacher:
        return None
    
    # Check if student is enrolled in any classes
    enrollments = Enrollment.objects.filter(student=user)
    
    if not enrollments.exists():
        # Individual student - can access all levels
        return None
    
    # Student enrolled in classes - can only access levels assigned to their classes
    qs = Level.objects.filter(classrooms__enrollments__student=user).distinct()
    return qs

@login_required
def dashboard(request):
    if request.user.is_teacher:
        classes = request.user.classes.all()
        return render(request, "maths/teacher_dashboard.html", {"classes": classes})
    allowed = student_allowed_levels(request.user)
    levels = allowed if allowed is not None else Level.objects.all()
    
    # Group levels by year and topics
    levels_by_year = {}
    for level in levels:
        year = level.level_number
        if year not in levels_by_year:
            levels_by_year[year] = []
        levels_by_year[year].append(level)
    
    # Sort years
    sorted_years = sorted(levels_by_year.keys())
    
    return render(request, "maths/student_dashboard.html", {
        "levels_by_year": levels_by_year,
        "sorted_years": sorted_years,
        "has_class": Enrollment.objects.filter(student=request.user).exists()
    })

@login_required
def topic_list(request):
    topics = Topic.objects.all()
    return render(request, "maths/topics.html", {"topics": topics})

@login_required
def level_list(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    allowed = student_allowed_levels(request.user)
    if allowed is None:
        levels = topic.levels.all()
    else:
        levels = topic.levels.filter(pk__in=allowed.values_list("pk", flat=True))
    return render(request, "maths/levels.html", {"topic": topic, "levels": levels})

@login_required
def level_detail(request, level_number):
    level = get_object_or_404(Level, level_number=level_number)
    allowed = student_allowed_levels(request.user)
    if allowed is not None and not allowed.filter(pk=level.pk).exists():
        return render(request, "maths/forbidden.html", status=403)
    
    # Get topics for this level
    topics = level.topics.all()
    
    return render(request, "maths/level_detail.html", {
        "level": level,
        "topics": topics
    })

@login_required
def create_class(request):
    if not request.user.is_teacher:
        return redirect("maths:dashboard")
    if request.method == "POST":
        form = CreateClassForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.teacher = request.user
            classroom.save()
            form.save_m2m()
            return redirect("maths:dashboard")
    else:
        form = CreateClassForm()
    return render(request, "maths/create_class.html", {"form": form})

def teacher_center_registration(request):
    """Handle teacher registration for creating a center/school"""
    if request.method == "POST":
        form = TeacherCenterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome! You can now create classes for {form.cleaned_data['center_name']}")
            return redirect("maths:dashboard")
    else:
        form = TeacherCenterRegistrationForm()
    return render(request, "maths/teacher_center_registration.html", {"form": form})

def individual_student_registration(request):
    """Handle individual student registration"""
    if request.method == "POST":
        form = IndividualStudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! You now have access to all levels.")
            return redirect("maths:dashboard")
    else:
        form = IndividualStudentRegistrationForm()
    return render(request, "maths/individual_student_registration.html", {"form": form})

@login_required
def bulk_student_registration(request):
    """Handle bulk student registration for teachers"""
    if not request.user.is_teacher:
        return redirect("maths:dashboard")
    
    if request.method == "POST":
        form = StudentBulkRegistrationForm(request.POST)
        if form.is_valid():
            students_data = form.cleaned_data['student_data']
            created_count = 0
            
            with transaction.atomic():
                for student_info in students_data:
                    try:
                        user = CustomUser.objects.create_user(
                            username=student_info['username'],
                            email=student_info['email'],
                            password=student_info['password'],
                            is_teacher=False
                        )
                        created_count += 1
                    except Exception as e:
                        messages.error(request, f"Failed to create user {student_info['username']}: {str(e)}")
            
            messages.success(request, f"Successfully created {created_count} student accounts.")
            return redirect("maths:dashboard")
    else:
        form = StudentBulkRegistrationForm()
    
    return render(request, "maths/bulk_student_registration.html", {"form": form})

@login_required
def join_class(request):
    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        try:
            classroom = ClassRoom.objects.get(code=code)
            Enrollment.objects.get_or_create(student=request.user, classroom=classroom)
            messages.success(request, f"Successfully joined class: {classroom.name}")
            return redirect("maths:dashboard")
        except ClassRoom.DoesNotExist:
            messages.error(request, "Invalid class code")
    return render(request, "maths/join_class.html")

@login_required
def add_question(request, level_number):
    """Add a new question to a specific level"""
    if not request.user.is_teacher:
        messages.error(request, "Only teachers can add questions.")
        return redirect("maths:dashboard")
    
    level = get_object_or_404(Level, level_number=level_number)
    
    if request.method == "POST":
        question_form = QuestionForm(request.POST)
        answer_formset = AnswerFormSet(request.POST)
        
        if question_form.is_valid() and answer_formset.is_valid():
            with transaction.atomic():
                # Save the question
                question = question_form.save(commit=False)
                question.level = level
                question.save()
                
                # Save the answers
                for form in answer_formset:
                    if form.cleaned_data.get('answer_text'):
                        answer = form.save(commit=False)
                        answer.question = question
                        answer.save()
                
                messages.success(request, f"Question added successfully to {level}!")
                return redirect("maths:level_questions", level_number=level.level_number)
    else:
        question_form = QuestionForm()
        answer_formset = AnswerFormSet()
    
    return render(request, "maths/add_question.html", {
        "question_form": question_form,
        "answer_formset": answer_formset,
        "level": level
    })

@login_required
def level_questions(request, level_number):
    """Display all questions for a specific level"""
    level = get_object_or_404(Level, level_number=level_number)
    questions = level.questions.all()
    
    return render(request, "maths/level_questions.html", {
        "level": level,
        "questions": questions
    })

@login_required
def take_quiz(request, level_number):
    """Allow students to take a quiz for a specific level"""
    level = get_object_or_404(Level, level_number=level_number)
    
    # Check if student has access to this level
    allowed = student_allowed_levels(request.user)
    if allowed is not None and not allowed.filter(pk=level.pk).exists():
        messages.error(request, "You don't have access to this level.")
        return redirect("maths:dashboard")
    
    # Get all questions for this level
    all_questions = list(level.questions.all())
    
    # Select random questions (limit to 10 questions)
    if len(all_questions) > 10:
        questions = random.sample(all_questions, 10)
    else:
        questions = all_questions
    
    # Shuffle the questions
    random.shuffle(questions)
    
    if request.method == "POST":
        score = 0
        total_points = 0
        
        for question in questions:
            total_points += question.points
            
            if question.question_type == 'multiple_choice':
                answer_id = request.POST.get(f'question_{question.id}')
                if answer_id:
                    try:
                        selected_answer = Answer.objects.get(id=answer_id, question=question)
                        is_correct = selected_answer.is_correct
                        if is_correct:
                            score += question.points
                        
                        # Save student answer
                        StudentAnswer.objects.update_or_create(
                            student=request.user,
                            question=question,
                            defaults={
                                'selected_answer': selected_answer,
                                'is_correct': is_correct,
                                'points_earned': question.points if is_correct else 0
                            }
                        )
                    except Answer.DoesNotExist:
                        pass
        
        messages.success(request, f"Quiz completed! Score: {score}/{total_points}")
        return redirect("maths:level_detail", level_number=level.level_number)
    
    return render(request, "maths/take_quiz.html", {
        "level": level,
        "questions": questions
    })

@login_required
def practice_questions(request, level_number):
    """Practice questions with random selection from all topics"""
    level = get_object_or_404(Level, level_number=level_number)
    
    # Check if student has access to this level
    allowed = student_allowed_levels(request.user)
    if allowed is not None and not allowed.filter(pk=level.pk).exists():
        messages.error(request, "You don't have access to this level.")
        return redirect("maths:dashboard")
    
    # Get all questions for this level
    all_questions = level.questions.all()
    
    # Select random questions (limit to 10 for practice)
    if all_questions.count() > 10:
        questions = random.sample(list(all_questions), 10)
    else:
        questions = list(all_questions)
    
    # Shuffle the questions
    random.shuffle(questions)
    
    return render(request, "maths/practice_questions.html", {
        "level": level,
        "questions": questions,
        "total_questions": all_questions.count()
    })

@login_required
def measurements_questions(request, level_number):
    """Show measurements questions one by one"""
    level = get_object_or_404(Level, level_number=level_number)
    
    # Check if student has access to this level
    allowed = student_allowed_levels(request.user)
    if allowed is not None and not allowed.filter(pk=level.pk).exists():
        messages.error(request, "You don't have access to this level.")
        return redirect("maths:dashboard")
    
    # Get measurements topic (for display purposes)
    measurements_topic = Topic.objects.filter(name="Measurements").first()
    if not measurements_topic:
        measurements_topic = Topic.objects.create(name="Measurements")
    
    # Get all measurements questions for this level
    all_questions = Question.objects.filter(level=level).order_by('id')
    
    # Get current question number from URL parameter (default to 1)
    question_number = int(request.GET.get('q', 1))
    
    # Start timer on first question load
    timer_session_key = "measurements_timer_start"
    timer_start = request.session.get(timer_session_key)
    if question_number == 1 and not timer_start:
        request.session[timer_session_key] = time.time()
    
    # Handle form submission
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'check_answer':
            question_id = request.POST.get('question_id')
            answer_id = request.POST.get('answer_id')
            text_answer = request.POST.get('text_answer')
            
            if question_id:
                try:
                    question = Question.objects.get(id=question_id, level=level)
                    
                    if answer_id:
                        # Multiple choice or true/false question
                        answer = Answer.objects.get(id=answer_id, question=question)
                        
                        # Save student answer
                        student_answer, created = StudentAnswer.objects.update_or_create(
                            student=request.user,
                            question=question,
                            defaults={
                                'selected_answer': answer,
                                'is_correct': answer.is_correct,
                                'points_earned': question.points if answer.is_correct else 0
                            }
                        )
                        
                        # Redirect to show result
                        return redirect(f"{request.path}?q={question_number}&checked=1&answer_id={answer_id}")
                    
                    elif text_answer and question.question_type == 'short_answer':
                        # Short answer question - for now, always mark as correct
                        # In a real system, you'd implement text matching logic
                        student_answer, created = StudentAnswer.objects.update_or_create(
                            student=request.user,
                            question=question,
                            defaults={
                                'text_answer': text_answer,
                                'is_correct': True,  # For demo purposes, always correct
                                'points_earned': question.points
                            }
                        )
                        
                        # Redirect to show result
                        return redirect(f"{request.path}?q={question_number}&checked=1&text_answer={text_answer}")
                    
                except (Question.DoesNotExist, Answer.DoesNotExist):
                    messages.error(request, "Invalid question or answer.")
        
        elif action == 'next_question':
            # Move to next question
            next_question = question_number + 1
            if next_question <= all_questions.count():
                return redirect(f"{request.path}?q={next_question}")
            else:
                # All questions completed - show score
                return redirect(f"{request.path}?completed=1")
    
    # Check if completed
    completed = request.GET.get('completed') == '1'
    
    if completed:
        # Calculate total score and time taken
        student_answers = StudentAnswer.objects.filter(
            student=request.user,
            question__level=level
        )
        total_score = sum(answer.points_earned for answer in student_answers)
        total_points = sum(q.points for q in all_questions)
        now_ts = time.time()
        start_ts = request.session.get(timer_session_key) or now_ts
        total_time_seconds = max(1, int(now_ts - start_ts))
        # Clear timer for next attempt
        if timer_session_key in request.session:
            del request.session[timer_session_key]
        # Compute points: percentage * 100 * 60 / time_seconds
        percentage = (total_score / total_points) if total_points else 0
        final_points = (percentage * 100 * 60) / total_time_seconds if total_time_seconds else 0
        # Round for display
        final_points = round(final_points, 2)
        
        return render(request, "maths/measurements_questions.html", {
            "level": level,
            "completed": True,
            "total_score": total_score,
            "total_points": total_points,
            "total_time_seconds": total_time_seconds,
            "final_points": final_points,
            "topic": measurements_topic,
            "student_answers": student_answers,
            "all_questions": all_questions
        })
    
    # Get current question
    if question_number <= all_questions.count():
        current_question = all_questions[question_number - 1]
    else:
        messages.error(request, "Question not found.")
        return redirect("maths:level_detail", level_number=level.level_number)
    
    # Check if answer was just checked
    checked = request.GET.get('checked') == '1'
    selected_answer_id = request.GET.get('answer_id')
    text_answer = request.GET.get('text_answer')
    selected_answer = None
    is_text_answer = False
    
    if checked and selected_answer_id:
        try:
            selected_answer = Answer.objects.get(id=selected_answer_id, question=current_question)
        except Answer.DoesNotExist:
            pass
    elif checked and text_answer:
        # For short answer questions, create a mock answer object
        class MockAnswer:
            def __init__(self, text, is_correct=True):
                self.answer_text = text
                self.is_correct = is_correct
        
        selected_answer = MockAnswer(text_answer, True)
        is_text_answer = True
    
    # Get student's previous answers for progress tracking
    student_answers = StudentAnswer.objects.filter(
        student=request.user,
        question__level=level
    )
    
    # Elapsed time for live timer
    start_ts = request.session.get(timer_session_key)
    elapsed_seconds = int(time.time() - start_ts) if start_ts else 0

    return render(request, "maths/measurements_questions.html", {
        "level": level,
        "current_question": current_question,
        "question_number": question_number,
        "total_questions": all_questions.count(),
        "topic": measurements_topic,
        "student_answers": student_answers,
        "checked": checked,
        "selected_answer": selected_answer,
        "is_text_answer": is_text_answer,
        "is_last_question": question_number == all_questions.count(),
        "elapsed_seconds": elapsed_seconds
    })
