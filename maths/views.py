from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
import time
from django.db.models import Q
import random
from datetime import datetime
import json
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
    
    # Separate Basic Facts levels (>= 100) from Year levels (< 100)
    # Basic Facts are always accessible to all students
    basic_facts_levels = Level.objects.filter(level_number__gte=100)
    year_levels = levels.filter(level_number__lt=100)
    
    # Group year levels by year and topics
    levels_by_year = {}
    for level in year_levels:
        year = level.level_number
        if year not in levels_by_year:
            levels_by_year[year] = []
        levels_by_year[year].append(level)
    
    # Sort years
    sorted_years = sorted(levels_by_year.keys())
    
    # Group Basic Facts levels by subtopic (Addition, Subtraction, etc.)
    basic_facts_by_subtopic = {}
    for level in basic_facts_levels:
        # Get the subtopic (Addition, Subtraction, etc.)
        subtopics = level.topics.filter(name__in=['Addition', 'Subtraction', 'Multiplication', 'Division'])
        if subtopics.exists():
            subtopic_name = subtopics.first().name
            if subtopic_name not in basic_facts_by_subtopic:
                basic_facts_by_subtopic[subtopic_name] = []
            basic_facts_by_subtopic[subtopic_name].append(level)
    
    # Sort Basic Facts levels within each subtopic by level_number
    for subtopic in basic_facts_by_subtopic:
        basic_facts_by_subtopic[subtopic].sort(key=lambda x: x.level_number)
    
    # Calculate student progress by level
    from django.db.models import Count, Min, Max, Avg, Sum
    
    # Get all student answers for all levels
    student_answers = StudentAnswer.objects.filter(
        student=request.user
    ).select_related('question', 'question__level')
    
    # Group by level and session_id to count attempts
    progress_by_level = []
    
    # Get unique combinations of level_number and session_id
    unique_level_sessions = student_answers.values('question__level__level_number', 'session_id').distinct()
    
    # Group by level
    level_data = {}
    for item in unique_level_sessions:
        level_num = item['question__level__level_number']
        session_id = item['session_id']
        
        if not session_id:  # Skip empty session_ids
            continue
            
        if level_num not in level_data:
            level_data[level_num] = set()
        
        level_data[level_num].add(session_id)
    
    # Calculate stats for each level
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    # For Basic Facts levels, use default of 10 questions
    for level_num, session_ids in level_data.items():
        attempts_data = []
        completed_session_ids = []
        question_limit = YEAR_QUESTION_COUNTS.get(level_num, 10)
        
        # Get level info
        try:
            level_obj = Level.objects.get(level_number=level_num)
            level_name = f"Level {level_num}" if level_num >= 100 else f"Year {level_num}"
        except Level.DoesNotExist:
            level_name = f"Level {level_num}"
        
        for session_id in session_ids:
            session_answers = student_answers.filter(
                session_id=session_id,
                question__level__level_number=level_num
            )
            # Count attempt only if a full quiz was completed for that level
            if session_answers.count() != question_limit:
                continue
            completed_session_ids.append(session_id)
            
            # Calculate points using the formula: percentage * 100 * 60 / time_seconds
            # Get the first answer to get time_taken_seconds and date for the session
            first_answer = session_answers.first()
            if first_answer and first_answer.time_taken_seconds > 0:
                total_correct = sum(1 for a in session_answers if a.is_correct)
                total_questions = session_answers.count()
                time_seconds = first_answer.time_taken_seconds
                
                percentage = (total_correct / total_questions) if total_questions else 0
                final_points = (percentage * 100 * 60) / time_seconds if time_seconds else 0
                attempts_data.append({
                    'points': round(final_points, 2),
                    'time_seconds': time_seconds,
                    'date': first_answer.answered_at
                })
            else:
                # Fallback: just sum points_earned if no time data
                total_points = sum(a.points_earned for a in session_answers)
                first_answer_date = first_answer.answered_at if first_answer else None
                attempts_data.append({
                    'points': total_points,
                    'time_seconds': 0,
                    'date': first_answer_date
                })
        
        if attempts_data:
            points_list = [a['points'] for a in attempts_data]
            # Get best score (highest points)
            best_score = max(points_list)
            # Get best attempt date
            best_attempt = max(attempts_data, key=lambda x: x['points'])
            
            progress_by_level.append({
                'level_number': level_num,
                'level_name': level_name,
                'total_attempts': len(completed_session_ids),
                'best_points': best_score,
                'best_time_seconds': best_attempt['time_seconds'],
                'best_date': best_attempt['date'],
                'min_points': min(points_list),
                'max_points': max(points_list),
                'avg_points': round(sum(points_list) / len(points_list), 1)
            })
    
    # Sort by level number
    progress_by_level.sort(key=lambda x: x['level_number'])
    
    return render(request, "maths/student_dashboard.html", {
        "levels_by_year": levels_by_year,
        "sorted_years": sorted_years,
        "basic_facts_by_subtopic": basic_facts_by_subtopic,
        "has_class": Enrollment.objects.filter(student=request.user).exists(),
        "progress_by_level": progress_by_level,
        "show_progress_table": True,
        "show_all_content": True
    })

@login_required
def dashboard_detail(request):
    """Detailed dashboard view showing progress table"""
    if request.user.is_teacher:
        classes = request.user.classes.all()
        return render(request, "maths/teacher_dashboard.html", {"classes": classes})
    allowed = student_allowed_levels(request.user)
    levels = allowed if allowed is not None else Level.objects.all()
    
    # Separate Basic Facts levels (>= 100) from Year levels (< 100)
    basic_facts_levels = Level.objects.filter(level_number__gte=100)
    year_levels = levels.filter(level_number__lt=100)
    
    # Group year levels by year and topics
    levels_by_year = {}
    for level in year_levels:
        year = level.level_number
        if year not in levels_by_year:
            levels_by_year[year] = []
        levels_by_year[year].append(level)
    
    # Sort years
    sorted_years = sorted(levels_by_year.keys())
    
    # Group Basic Facts levels by subtopic
    basic_facts_by_subtopic = {}
    for level in basic_facts_levels:
        subtopics = level.topics.filter(name__in=['Addition', 'Subtraction', 'Multiplication', 'Division'])
        if subtopics.exists():
            subtopic_name = subtopics.first().name
            if subtopic_name not in basic_facts_by_subtopic:
                basic_facts_by_subtopic[subtopic_name] = []
            basic_facts_by_subtopic[subtopic_name].append(level)
    
    for subtopic in basic_facts_by_subtopic:
        basic_facts_by_subtopic[subtopic].sort(key=lambda x: x.level_number)
    
    # Calculate student progress by level (same as dashboard)
    from django.db.models import Count, Min, Max, Avg, Sum
    
    # Get all student answers for all levels
    student_answers = StudentAnswer.objects.filter(
        student=request.user
    ).select_related('question', 'question__level')
    
    # Group by level and session_id to count attempts
    progress_by_level = []
    
    # Get unique combinations of level_number and session_id
    unique_level_sessions = student_answers.values('question__level__level_number', 'session_id').distinct()
    
    # Group by level
    level_data = {}
    for item in unique_level_sessions:
        level_num = item['question__level__level_number']
        session_id = item['session_id']
        
        if not session_id:  # Skip empty session_ids
            continue
            
        if level_num not in level_data:
            level_data[level_num] = set()
        
        level_data[level_num].add(session_id)
    
    # Calculate stats for each level
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    for level_num, session_ids in level_data.items():
        attempts_data = []
        completed_session_ids = []
        question_limit = YEAR_QUESTION_COUNTS.get(level_num, 10)
        
        # Get level info
        try:
            level_obj = Level.objects.get(level_number=level_num)
            level_name = f"Level {level_num}" if level_num >= 100 else f"Year {level_num}"
        except Level.DoesNotExist:
            level_name = f"Level {level_num}"
        
        for session_id in session_ids:
            session_answers = student_answers.filter(
                session_id=session_id,
                question__level__level_number=level_num
            )
            # Only count full attempts (completed all questions for that level)
            if session_answers.count() != question_limit:
                continue
            completed_session_ids.append(session_id)
            
            # Calculate points using the formula: percentage * 100 * 60 / time_seconds
            first_answer = session_answers.first()
            if first_answer and first_answer.time_taken_seconds > 0:
                total_correct = sum(1 for a in session_answers if a.is_correct)
                total_questions = session_answers.count()
                time_seconds = first_answer.time_taken_seconds
                
                percentage = (total_correct / total_questions) if total_questions else 0
                final_points = (percentage * 100 * 60) / time_seconds if time_seconds else 0
                attempts_data.append({
                    'points': round(final_points, 2),
                    'time_seconds': time_seconds,
                    'date': first_answer.answered_at
                })
            else:
                total_points = sum(a.points_earned for a in session_answers)
                first_answer_date = first_answer.answered_at if first_answer else None
                attempts_data.append({
                    'points': total_points,
                    'time_seconds': 0,
                    'date': first_answer_date
                })
        
        if attempts_data:
            points_list = [a['points'] for a in attempts_data]
            best_score = max(points_list)
            best_attempt = max(attempts_data, key=lambda x: x['points'])
            
            progress_by_level.append({
                'level_number': level_num,
                'level_name': level_name,
                'total_attempts': len(completed_session_ids),
                'best_points': best_score,
                'best_time_seconds': best_attempt['time_seconds'],
                'best_date': best_attempt['date'],
                'min_points': min(points_list),
                'max_points': max(points_list),
                'avg_points': round(sum(points_list) / len(points_list), 1)
            })
    
    # Sort by level number
    progress_by_level.sort(key=lambda x: x['level_number'])
    
    # Get Basic Facts progress from session
    basic_facts_progress = {}
    for subtopic_name, levels in basic_facts_by_subtopic.items():
        basic_facts_progress[subtopic_name] = []
        for level in levels:
            level_num = level.level_number
            results_key = f"basic_facts_results_{request.user.id}_{level_num}"
            results_list = request.session.get(results_key, [])
            
            if results_list:
                # Get best result
                best_result = max(results_list, key=lambda x: x['points'])
                
                # Fix old format points (divide by 10 if > 100, indicating old format)
                best_points = best_result['points']
                if best_points > 100:
                    best_points = best_points / 10
                    # Update the stored value for future use - update all entries in the list
                    for idx, result in enumerate(results_list):
                        if result.get('points', 0) > 100:
                            results_list[idx]['points'] = result['points'] / 10
                    request.session[results_key] = results_list
                
                display_level = level_num
                if 100 <= level_num <= 106:  # Addition
                    display_level = level_num - 99
                elif 107 <= level_num <= 113:  # Subtraction
                    display_level = level_num - 106
                elif 114 <= level_num <= 120:  # Multiplication
                    display_level = level_num - 113
                elif 121 <= level_num <= 127:  # Division
                    display_level = level_num - 120
                
                basic_facts_progress[subtopic_name].append({
                    'display_level': display_level,
                    'level_number': level_num,
                    'best_points': best_points,
                    'best_time_seconds': best_result['time_taken_seconds'],
                    'best_date': datetime.fromisoformat(best_result['date']) if isinstance(best_result['date'], str) else best_result['date'],
                    'total_attempts': len(results_list)
                })
        
        # Sort by display_level
        basic_facts_progress[subtopic_name].sort(key=lambda x: x['display_level'])
    
    return render(request, "maths/student_dashboard.html", {
        "levels_by_year": levels_by_year,
        "sorted_years": sorted_years,
        "basic_facts_by_subtopic": basic_facts_by_subtopic,
        "basic_facts_progress": basic_facts_progress,
        "has_class": Enrollment.objects.filter(student=request.user).exists(),
        "progress_by_level": progress_by_level,
        "show_progress_table": True,
        "show_all_content": False
    })

@login_required
def measurements_progress(request, level_number):
    """Show detailed measurements progress with attempt history and graph"""
    level = get_object_or_404(Level, level_number=level_number)
    
    # Check if student has access to this level
    allowed = student_allowed_levels(request.user)
    if allowed is not None and not allowed.filter(pk=level.pk).exists():
        messages.error(request, "You don't have access to this level.")
        return redirect("maths:dashboard")
    
    # Get all student answers for Measurements topic for this level
    student_answers = StudentAnswer.objects.filter(
        student=request.user,
        question__level=level,
        question__level__topics__name="Measurements"
    ).select_related('question', 'question__level').order_by('answered_at')
    
    # Question limits per year
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    question_limit = YEAR_QUESTION_COUNTS.get(level_number, 10)
    
    # Get unique session IDs for this level
    unique_sessions = student_answers.values_list('session_id', flat=True).distinct()
    unique_sessions = [s for s in unique_sessions if s]  # Filter out empty strings
    
    # Build attempt history
    attempt_history = []
    for session_id in unique_sessions:
        session_answers = student_answers.filter(session_id=session_id)
        
        # Only count completed attempts
        if session_answers.count() != question_limit:
            continue
        
        # Calculate points for this attempt
        first_answer = session_answers.first()
        if first_answer and first_answer.time_taken_seconds > 0:
            total_correct = sum(1 for a in session_answers if a.is_correct)
            total_questions = session_answers.count()
            time_seconds = first_answer.time_taken_seconds
            
            percentage = (total_correct / total_questions) if total_questions else 0
            final_points = (percentage * 100 * 60) / time_seconds if time_seconds else 0
            points = round(final_points, 2)
        else:
            points = sum(a.points_earned for a in session_answers)
        
        # Get attempt date
        attempt_date = session_answers.first().answered_at if session_answers.exists() else None
        
        attempt_history.append({
            'session_id': session_id,
            'attempt_number': len(attempt_history) + 1,
            'points': points,
            'date': attempt_date
        })
    
    # Sort by date
    attempt_history.sort(key=lambda x: x['date'] if x['date'] else datetime.min)
    
    # Re-number attempts after sorting
    for i, attempt in enumerate(attempt_history):
        attempt['attempt_number'] = i + 1
    
    # Calculate stats
    if attempt_history:
        points_list = [a['points'] for a in attempt_history]
        stats = {
            'total_attempts': len(attempt_history),
            'min_points': min(points_list),
            'max_points': max(points_list),
            'avg_points': round(sum(points_list) / len(points_list), 2)
        }
        
        # Prepare data for graph (attempt numbers and points)
        graph_data = {
            'attempt_numbers': [a['attempt_number'] for a in attempt_history],
            'points': points_list,
            'dates': [a['date'].strftime('%Y-%m-%d') if a['date'] else '' for a in attempt_history]
        }
    else:
        stats = {
            'total_attempts': 0,
            'min_points': 0,
            'max_points': 0,
            'avg_points': 0
        }
        graph_data = {
            'attempt_numbers': [],
            'points': [],
            'dates': []
        }
    
    # Convert graph data to JSON for JavaScript
    graph_data_json = {
        'attempt_numbers': json.dumps(graph_data['attempt_numbers']),
        'points': json.dumps(graph_data['points']),
        'dates': json.dumps(graph_data['dates'])
    }
    
    return render(request, "maths/measurements_progress.html", {
        "level": level,
        "attempt_history": attempt_history,
        "stats": stats,
        "graph_data": graph_data_json
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

def generate_basic_facts_question(level_num):
    """Generate a single question for Basic Facts levels"""
    if 100 <= level_num <= 106:  # Addition
        if level_num == 100:
            a, b = random.randint(1, 5), random.randint(1, 5)
            return f"{a} + {b} = ?", str(a + b)
        elif level_num == 101:
            a, b = random.randint(0, 9), random.randint(0, 9)
            return f"{a} + {b} = ?", str(a + b)
        elif level_num == 102:
            # No carry over
            a1, a2 = random.randint(1, 4), random.randint(0, 4)
            b1, b2 = random.randint(1, 4), random.randint(0, 9 - a2)
            a, b = a1 * 10 + a2, b1 * 10 + b2
            return f"{a} + {b} = ?", str(a + b)
        elif level_num == 103:
            # With carry over
            a = random.randint(15, 99)
            a_units = a % 10
            b_tens = random.randint(1, 8)
            b_units = random.randint(max(1, 10 - a_units), 9)
            b = b_tens * 10 + b_units
            return f"{a} + {b} = ?", str(a + b)
        elif level_num == 104:
            a, b = random.randint(100, 999), random.randint(100, 999)
            return f"{a} + {b} = ?", str(a + b)
        elif level_num == 105:
            a, b = random.randint(1000, 9999), random.randint(1000, 9999)
            return f"{a} + {b} = ?", str(a + b)
        elif level_num == 106:
            a, b = random.randint(10000, 99999), random.randint(10000, 99999)
            return f"{a} + {b} = ?", str(a + b)
    
    elif 107 <= level_num <= 113:  # Subtraction
        if level_num == 107:
            a = random.randint(5, 9)
            b = random.randint(1, a)
            return f"{a} - {b} = ?", str(a - b)
        elif level_num == 108:
            a = random.randint(10, 99)
            a_units = a % 10
            b = random.randint(0, a_units)
            return f"{a} - {b} = ?", str(a - b)
        elif level_num == 109:
            a = random.randint(10, 99)
            a_units = a % 10
            b = random.randint(a_units + 1, 9)
            return f"{a} - {b} = ?", str(a - b)
        elif level_num == 110:
            a = random.randint(20, 99)
            b = random.randint(10, a)
            return f"{a} - {b} = ?", str(a - b)
        elif level_num == 111:
            a, b = random.randint(10, 99), random.randint(10, 99)
            return f"{a} - {b} = ?", str(a - b)
        elif level_num == 112:
            a = random.randint(100, 999)
            b = random.randint(100, a)
            return f"{a} - {b} = ?", str(a - b)
        elif level_num == 113:
            a = random.randint(1000, 9999)
            b = random.randint(1000, a)
            return f"{a} - {b} = ?", str(a - b)
    
    elif 114 <= level_num <= 120:  # Multiplication
        if level_num == 114:
            multiplier = random.choice([1, 10])
            base = random.randint(1, 99)
            return f"{base} × {multiplier} = ?", str(base * multiplier)
        elif level_num == 115:
            multiplier = random.choice([1, 10, 100])
            base = random.randint(1, 99)
            return f"{base} × {multiplier} = ?", str(base * multiplier)
        elif level_num == 116:
            multiplier = random.choice([5, 10])
            base = random.randint(1, 99)
            return f"{base} × {multiplier} = ?", str(base * multiplier)
        elif level_num == 117:
            multiplier = random.choice([2, 3, 5, 10])
            base = random.randint(1, 99)
            return f"{base} × {multiplier} = ?", str(base * multiplier)
        elif level_num == 118:
            multiplier = random.choice([2, 3, 4, 5, 10])
            base = random.randint(10, 999)
            return f"{base} × {multiplier} = ?", str(base * multiplier)
        elif level_num == 119:
            multiplier = random.choice([2, 3, 4, 5, 6, 7, 10])
            base = random.randint(10, 999)
            return f"{base} × {multiplier} = ?", str(base * multiplier)
        elif level_num == 120:
            multiplier = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10])
            base = random.randint(100, 999)
            return f"{base} × {multiplier} = ?", str(base * multiplier)
    
    elif 121 <= level_num <= 127:  # Division
        if level_num == 121:
            divisor = random.choice([1, 10])
            if divisor == 10:
                quotient = random.randint(1, 9)
                dividend = quotient * 10
            else:
                dividend = random.randint(10, 99)
                quotient = dividend
            return f"{dividend} ÷ {divisor} = ?", str(quotient)
        elif level_num == 122:
            divisor = random.choice([1, 10, 100])
            if divisor == 100:
                quotient = random.randint(1, 9)
                dividend = quotient * 100
            elif divisor == 10:
                quotient = random.randint(10, 99)
                dividend = quotient * 10
            else:
                dividend = random.randint(100, 999)
                quotient = dividend
            return f"{dividend} ÷ {divisor} = ?", str(quotient)
        elif level_num == 123:
            divisor = random.choice([5, 10])
            quotient = random.randint(10, 99) if divisor == 10 else random.randint(10, 199)
            dividend = quotient * divisor
            return f"{dividend} ÷ {divisor} = ?", str(quotient)
        elif level_num == 124:
            divisor = random.choice([2, 3, 5, 10])
            quotient = random.randint(10, 99)
            dividend = quotient * divisor
            return f"{dividend} ÷ {divisor} = ?", str(quotient)
        elif level_num == 125:
            divisor = random.choice([2, 3, 4, 5, 10])
            quotient = random.randint(10, 99)
            dividend = quotient * divisor
            return f"{dividend} ÷ {divisor} = ?", str(quotient)
        elif level_num == 126:
            divisor = random.choice([2, 3, 4, 5, 6, 7, 10])
            quotient = random.randint(10, 99)
            dividend = quotient * divisor
            return f"{dividend} ÷ {divisor} = ?", str(quotient)
        elif level_num == 127:
            divisor = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
            quotient = random.randint(10, 99)
            dividend = quotient * divisor
            return f"{dividend} ÷ {divisor} = ?", str(quotient)
    
    return None, None

class DynamicQuestion:
    """Simple class to mimic Question object for Basic Facts"""
    def __init__(self, question_text, correct_answer, question_id):
        self.id = question_id
        self.question_text = question_text
        self.correct_answer = correct_answer
        self.question_type = 'short_answer'
        self.points = 1
        self.image = None
        self.explanation = None
        self.answers = type('obj', (object,), {'all': lambda: []})()

@login_required
def basic_facts_subtopic(request, subtopic_name):
    """Show level selection page for a Basic Facts subtopic"""
    # Validate subtopic name
    valid_subtopics = ['Addition', 'Subtraction', 'Multiplication', 'Division']
    if subtopic_name not in valid_subtopics:
        messages.error(request, "Invalid subtopic.")
        return redirect("maths:dashboard")
    
    # Get all levels for this subtopic
    topic = get_object_or_404(Topic, name=subtopic_name)
    levels = Level.objects.filter(
        topics=topic,
        level_number__gte=100
    ).order_by('level_number')
    
    # Handle form submission
    if request.method == 'POST':
        level_number = request.POST.get('level_number')
        if level_number:
            try:
                level = Level.objects.get(level_number=int(level_number), topics=topic)
                return redirect('maths:take_quiz', level_number=level.level_number)
            except (Level.DoesNotExist, ValueError):
                messages.error(request, "Invalid level selected.")
    
    # Get subtopic icon
    subtopic_icons = {
        'Addition': '➕',
        'Subtraction': '➖',
        'Multiplication': '✖️',
        'Division': '➗'
    }
    
    return render(request, "maths/basic_facts_subtopic.html", {
        "subtopic_name": subtopic_name,
        "levels": levels,
        "subtopic_icon": subtopic_icons.get(subtopic_name, '🧮')
    })

@login_required
def take_quiz(request, level_number):
    """Allow students to take a quiz for a specific level"""
    level = get_object_or_404(Level, level_number=level_number)
    
    # Check if student has access to this level
    # Basic Facts levels (>= 100) are always accessible to all students
    if level_number < 100:
        allowed = student_allowed_levels(request.user)
        if allowed is not None and not allowed.filter(pk=level.pk).exists():
            messages.error(request, "You don't have access to this level.")
            return redirect("maths:dashboard")
    
    # For Basic Facts levels, generate questions dynamically
    is_basic_facts = level_number >= 100
    session_questions_key = f"quiz_questions_{level_number}"
    
    # Timer handling - start timer on first load
    timer_session_key = f"quiz_timer_{level_number}"
    timer_start = request.session.get(timer_session_key)
    
    if is_basic_facts:
        if request.method == "GET":
            # Generate 10 questions
            questions_data = []
            for i in range(10):
                q_text, correct_answer = generate_basic_facts_question(level_number)
                if q_text:
                    questions_data.append({
                        'text': q_text,
                        'correct_answer': correct_answer,
                        'index': i
                    })
            request.session[session_questions_key] = questions_data
            
            # Create DynamicQuestion objects for template
            questions = [DynamicQuestion(q['text'], q['correct_answer'], q['index']) for q in questions_data]
        else:
            # POST - retrieve from session
            questions_data = request.session.get(session_questions_key, [])
            questions = [DynamicQuestion(q['text'], q['correct_answer'], q['index']) for q in questions_data]
    else:
        # Get all questions for this level from database
        all_questions = list(level.questions.all())
        
        # Select random questions (limit to 10 questions)
        if len(all_questions) > 10:
            questions = random.sample(all_questions, 10)
        else:
            questions = all_questions
        
        # Shuffle the questions
        random.shuffle(questions)
    
    if request.method == "POST":
        # Get time elapsed
        now_ts = time.time()
        start_ts = request.session.get(timer_session_key, now_ts)
        time_taken_seconds = max(1, int(now_ts - start_ts))
        
        score = 0
        total_points = 0
        # Create a session id for this quiz attempt to track best records
        import uuid
        session_id = str(uuid.uuid4())
        
        for question in questions:
            total_points += question.points
            
            if is_basic_facts:
                # Handle dynamic Basic Facts questions
                student_answer = request.POST.get(f'question_{question.id}', '').strip()
                # Normalize answer (remove spaces, handle negative signs)
                student_answer_normalized = student_answer.replace(' ', '')
                correct_answer_normalized = question.correct_answer.replace(' ', '')
                
                is_correct = (student_answer_normalized == correct_answer_normalized)
                if is_correct:
                    score += question.points
                
                # For Basic Facts, we don't store in DB, just track in session
                # We'll handle scoring without creating DB records
            elif question.question_type == 'multiple_choice':
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
                                'points_earned': question.points if is_correct else 0,
                                'session_id': session_id,
                                'time_taken_seconds': time_taken_seconds
                            }
                        )
                    except Answer.DoesNotExist:
                        pass
        
        # For Basic Facts, store session results for tracking best scores
        if is_basic_facts:
            # Store result with user ID and level number for persistence
            basic_facts_results_key = f"basic_facts_results_{request.user.id}_{level_number}"
            results_list = request.session.get(basic_facts_results_key, [])
            
            # Calculate points same as measurements, but divide by 10 for Basic Facts
            percentage = (score / total_points) if total_points else 0
            final_points_calc = ((percentage * 100 * 60) / time_taken_seconds) / 10 if time_taken_seconds else 0
            
            result_entry = {
                'session_id': session_id,
                'score': score,
                'total_points': total_points,
                'time_taken_seconds': time_taken_seconds,
                'points': round(final_points_calc, 2),
                'date': datetime.now().isoformat()
            }
            
            results_list.append(result_entry)
            request.session[basic_facts_results_key] = results_list
            
            # Also store individual session result for comparison
            session_results_key = f"quiz_results_{level_number}_{session_id}"
            request.session[session_results_key] = {
                'score': score,
                'total_points': total_points,
                'time_taken_seconds': time_taken_seconds
            }
            
            # Clear questions from session
            if session_questions_key in request.session:
                del request.session[session_questions_key]
        
        # Clear timer from session
        if timer_session_key in request.session:
            del request.session[timer_session_key]
        
        # Calculate points using the formula: percentage * 100 * 60 / time_seconds
        # For Basic Facts, divide by 10
        percentage = (score / total_points) if total_points else 0
        if is_basic_facts:
            final_points = ((percentage * 100 * 60) / time_taken_seconds) / 10 if time_taken_seconds else 0
        else:
            final_points = (percentage * 100 * 60) / time_taken_seconds if time_taken_seconds else 0
        final_points = round(final_points, 2)
        
        # Compute previous best record for this level
        if is_basic_facts:
            # For Basic Facts, check session-based results
            previous_best_points = None
            # Look through all session keys for this level
            for key in list(request.session.keys()):
                if key.startswith(f"quiz_results_{level_number}_"):
                    result_data = request.session.get(key, {})
                    if result_data:
                        result_score = result_data.get('score', 0)
                        result_total = result_data.get('total_points', 10)
                        result_time = result_data.get('time_taken_seconds', 1)
                        result_percentage = (result_score / result_total) if result_total else 0
                        # For Basic Facts, divide by 10
                        result_points = ((result_percentage * 100 * 60) / result_time) / 10 if result_time else 0
                        
                        if previous_best_points is None or result_points > previous_best_points:
                            previous_best_points = result_points
        else:
            # For regular levels, check database records
            previous_sessions = StudentAnswer.objects.filter(
                student=request.user,
                question__level=level
            ).exclude(session_id=session_id).values_list('session_id', flat=True).distinct()

            previous_best_points = None
            for sid in previous_sessions:
                if not sid:
                    continue
                # Get all answers for this session
                session_answers = StudentAnswer.objects.filter(
                    student=request.user,
                    question__level=level,
                    session_id=sid
                )
                if not session_answers.exists():
                    continue
                # Calculate points for this session using the same formula
                first_answer = session_answers.first()
                if first_answer and first_answer.time_taken_seconds > 0:
                    session_correct = sum(1 for a in session_answers if a.is_correct)
                    session_total = session_answers.count()
                    session_time = first_answer.time_taken_seconds
                    session_percentage = (session_correct / session_total) if session_total else 0
                    session_points = (session_percentage * 100 * 60) / session_time if session_time else 0
                else:
                    session_points = sum(a.points_earned for a in session_answers)
                
                if previous_best_points is None or session_points > previous_best_points:
                    previous_best_points = session_points

        # For Basic Facts, show completion screen like measurements
        if is_basic_facts:
            beat_record = previous_best_points is not None and final_points > previous_best_points
            is_first_attempt = previous_best_points is None
            
            return render(request, "maths/take_quiz.html", {
                "level": level,
                "completed": True,
                "total_score": score,
                "total_points": total_points,
                "total_time_seconds": time_taken_seconds,
                "final_points": final_points,
                "previous_best_points": round(previous_best_points, 2) if previous_best_points is not None else None,
                "beat_record": beat_record,
                "is_first_attempt": is_first_attempt
            })
        
        # For regular levels, show messages and redirect
        if previous_best_points is None:
            messages.success(request, f"Quiz completed! You scored {final_points} points. New high score received!")
        elif final_points > previous_best_points:
            messages.success(request, f"🎉 You beat your record! New high score received: {final_points} points (previous best was {round(previous_best_points, 2)}).")
        else:
            messages.info(request, f"Quiz completed! You scored {final_points} points. Best record remains {round(previous_best_points, 2)} points.")
        return redirect("maths:dashboard")
    
    # Start timer on first load
    if not timer_start:
        request.session[timer_session_key] = time.time()
    
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
    all_questions_query = Question.objects.filter(level=level)
    
    # Question limits per year
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    question_limit = YEAR_QUESTION_COUNTS.get(level.level_number, 10)
    
    # Get current question number from URL parameter (default to 1)
    question_number = int(request.GET.get('q', 1))
    
    # Start timer on first question load and create session
    timer_session_key = "measurements_timer_start"
    questions_session_key = "measurements_question_ids"
    timer_start = request.session.get(timer_session_key)
    
    if question_number == 1 and not timer_start:
        request.session[timer_session_key] = time.time()
        # Generate a unique session ID for this attempt
        import uuid
        request.session['current_attempt_id'] = str(uuid.uuid4())
        
        # Select random questions for this attempt
        all_questions_list = list(all_questions_query)
        if len(all_questions_list) > question_limit:
            selected_questions = random.sample(all_questions_list, question_limit)
        else:
            selected_questions = all_questions_list
        
        # Randomize the order
        random.shuffle(selected_questions)
        
        # Store question IDs in session
        request.session[questions_session_key] = [q.id for q in selected_questions]
    
    # Get question IDs from session
    question_ids = request.session.get(questions_session_key, [])
    
    # Get all questions from the stored IDs
    all_questions = Question.objects.filter(id__in=question_ids).order_by(
        'id'  # This won't work as expected, we need to preserve order
    )
    
    # Convert to list and maintain the order from session
    if question_ids:
        all_questions = [Question.objects.get(id=qid) for qid in question_ids]
    else:
        # Fallback if no session
        all_questions = []
    
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
                        
                        # Save student answer with session ID
                        attempt_id = request.session.get('current_attempt_id', '')
                        student_answer, created = StudentAnswer.objects.update_or_create(
                            student=request.user,
                            question=question,
                            defaults={
                                'selected_answer': answer,
                                'is_correct': answer.is_correct,
                                'points_earned': question.points if answer.is_correct else 0,
                                'session_id': attempt_id
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
            if next_question <= len(all_questions):
                return redirect(f"{request.path}?q={next_question}")
            else:
                # All questions completed - show score
                return redirect(f"{request.path}?completed=1")
    
    # Check if completed
    completed = request.GET.get('completed') == '1'
    
    if completed:
        # Calculate total score and time taken
        attempt_id = request.session.get('current_attempt_id', '')
        student_answers = StudentAnswer.objects.filter(
            student=request.user,
            question__level=level,
            session_id=attempt_id
        )
        total_score = sum(answer.points_earned for answer in student_answers)
        total_points = sum(q.points for q in all_questions)
        now_ts = time.time()
        start_ts = request.session.get(timer_session_key) or now_ts
        total_time_seconds = max(1, int(now_ts - start_ts))
        
        # Store time_taken_seconds for all answers in this session
        student_answers.update(time_taken_seconds=total_time_seconds)
        
        # Clear timer and question list for next attempt
        if timer_session_key in request.session:
            del request.session[timer_session_key]
        if questions_session_key in request.session:
            del request.session[questions_session_key]
        if 'current_attempt_id' in request.session:
            del request.session['current_attempt_id']
        # Compute points: percentage * 100 * 60 / time_seconds
        percentage = (total_score / total_points) if total_points else 0
        final_points = (percentage * 100 * 60) / total_time_seconds if total_time_seconds else 0
        # Round for display
        final_points = round(final_points, 2)
        
        # Compute previous best record for this level
        attempt_id = request.session.get('current_attempt_id', '')
        previous_sessions = StudentAnswer.objects.filter(
            student=request.user,
            question__level=level
        ).exclude(session_id=attempt_id).values_list('session_id', flat=True).distinct()

        previous_best_points = None
        for sid in previous_sessions:
            if not sid:
                continue
            session_answers = StudentAnswer.objects.filter(
                student=request.user,
                question__level=level,
                session_id=sid
            )
            if not session_answers.exists():
                continue
            first_answer = session_answers.first()
            if first_answer and first_answer.time_taken_seconds > 0:
                session_correct = sum(1 for a in session_answers if a.is_correct)
                session_total = session_answers.count()
                session_time = first_answer.time_taken_seconds
                session_percentage = (session_correct / session_total) if session_total else 0
                session_points = (session_percentage * 100 * 60) / session_time if session_time else 0
            else:
                session_points = sum(a.points_earned for a in session_answers)
            
            if previous_best_points is None or session_points > previous_best_points:
                previous_best_points = session_points
        
        beat_record = previous_best_points is not None and final_points > previous_best_points
        is_first_attempt = previous_best_points is None
        
        return render(request, "maths/measurements_questions.html", {
            "level": level,
            "completed": True,
            "total_score": total_score,
            "total_points": total_points,
            "total_time_seconds": total_time_seconds,
            "final_points": final_points,
            "topic": measurements_topic,
            "student_answers": student_answers,
            "all_questions": all_questions,
            "previous_best_points": round(previous_best_points, 2) if previous_best_points is not None else None,
            "beat_record": beat_record,
            "is_first_attempt": is_first_attempt
        })
    
    # Get current question
    if question_number <= len(all_questions):
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
        "total_questions": len(all_questions),
        "topic": measurements_topic,
        "student_answers": student_answers,
        "checked": checked,
        "selected_answer": selected_answer,
        "is_text_answer": is_text_answer,
        "is_last_question": question_number == len(all_questions),
        "elapsed_seconds": elapsed_seconds
    })
