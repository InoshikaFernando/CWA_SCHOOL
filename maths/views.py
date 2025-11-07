from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import time
from django.db.models import Q
import random
from datetime import datetime
import json
from .models import Topic, Level, ClassRoom, Enrollment, CustomUser, Question, Answer, StudentAnswer, BasicFactsResult, TimeLog
from .forms import CreateClassForm, StudentSignUpForm, TeacherSignUpForm, TeacherCenterRegistrationForm, IndividualStudentRegistrationForm, StudentBulkRegistrationForm, QuestionForm, AnswerFormSet, UserProfileForm, UserPasswordChangeForm

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
        subtopics = level.topics.filter(name__in=['Addition', 'Subtraction', 'Multiplication', 'Division', 'Place Value Facts'])
        if subtopics.exists():
            subtopic_name = subtopics.first().name
            if subtopic_name not in basic_facts_by_subtopic:
                basic_facts_by_subtopic[subtopic_name] = []
            basic_facts_by_subtopic[subtopic_name].append(level)
    
    # Sort Basic Facts levels within each subtopic by level_number
    for subtopic in basic_facts_by_subtopic:
        basic_facts_by_subtopic[subtopic].sort(key=lambda x: x.level_number)
    
    # Note: Progress calculation removed from home page - only shown on /dashboard/ page
    
    return render(request, "maths/student_dashboard.html", {
        "levels_by_year": levels_by_year,
        "sorted_years": sorted_years,
        "basic_facts_by_subtopic": basic_facts_by_subtopic,
        "has_class": Enrollment.objects.filter(student=request.user).exists(),
        "progress_by_level": [],
        "show_progress_table": False,
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
        subtopics = level.topics.filter(name__in=['Addition', 'Subtraction', 'Multiplication', 'Division', 'Place Value Facts'])
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
    ).select_related('question', 'question__level', 'question__topic')
    
    # Group by level, topic, and session_id to count attempts
    # This allows us to show separate entries for Measurements and Place Values
    progress_by_level = []
    
    # Get unique combinations of level_number, topic, and session_id
    # We need to determine topic from question patterns
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    
    # Group by level, topic, and session together
    # This ensures each unique combination gets its own entry
    # Filter out answers without topics first
    student_answers_with_topics = student_answers.filter(question__topic__isnull=False)
    
    unique_level_topic_sessions = student_answers_with_topics.values(
        'question__level__level_number', 
        'question__topic__name',
        'session_id'
    ).distinct()
    
    # Group by level and topic combination
    level_topic_data = {}
    for item in unique_level_topic_sessions:
        level_num = item['question__level__level_number']
        topic_name = item['question__topic__name']
        session_id = item['session_id']
        
        if not session_id or not topic_name:  # Skip empty session_ids or topics
            continue
        
        # Create unique key for level + topic combination
        key = (level_num, topic_name)
        if key not in level_topic_data:
            level_topic_data[key] = set()
        level_topic_data[key].add(session_id)
    
    # Calculate stats for each level + topic combination
    for (level_num, topic_name), session_ids in level_topic_data.items():
        attempts_data = []
        completed_session_ids = []
        
        # Get level info
        try:
            level_obj = Level.objects.get(level_number=level_num)
            level_name = f"Level {level_num}" if level_num >= 100 else f"Year {level_num}"
        except Level.DoesNotExist:
            level_name = f"Level {level_num}"
            topic_name = "Unknown"
        
        # Get the actual number of questions available for this topic/level
        try:
            topic_obj = Topic.objects.get(name=topic_name)
            available_questions = Question.objects.filter(
                level=level_obj,
                topic=topic_obj
            ).count()
        except (Topic.DoesNotExist, Level.DoesNotExist):
            available_questions = 0
        
        # Use the minimum of: standard limit OR all available questions
        standard_limit = YEAR_QUESTION_COUNTS.get(level_num, 10)
        question_limit = min(available_questions, standard_limit) if available_questions > 0 else standard_limit
        
        for session_id in session_ids:
            # Filter by level, topic, and session_id directly
            session_answers = student_answers_with_topics.filter(
                session_id=session_id,
                question__level__level_number=level_num,
                question__topic__name=topic_name
            )
            
            # Only count full attempts (completed all questions for that topic/level)
            # Require either the standard limit OR all available questions, whichever is minimum
            answer_count = session_answers.count()
            if answer_count < question_limit:
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
                'topic_name': topic_name,
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
    
    # Get Basic Facts progress from database
    basic_facts_progress = {}
    for subtopic_name, levels in basic_facts_by_subtopic.items():
        basic_facts_progress[subtopic_name] = []
        for level in levels:
            level_num = level.level_number
            
            # Get all attempts from database for this level
            db_results = BasicFactsResult.objects.filter(
                student=request.user,
                level=level
            ).order_by('-points')
            
            if db_results.exists():
                # Get best result (highest points)
                best_result = db_results.first()
                
                display_level = level_num
                if 100 <= level_num <= 106:  # Addition
                    display_level = level_num - 99
                elif 107 <= level_num <= 113:  # Subtraction
                    display_level = level_num - 106
                elif 114 <= level_num <= 120:  # Multiplication
                    display_level = level_num - 113
                elif 121 <= level_num <= 127:  # Division
                    display_level = level_num - 120
                elif 128 <= level_num <= 132:  # Place Value Facts
                    display_level = level_num - 127
                
                # Count total attempts (unique sessions)
                total_attempts = db_results.values('session_id').distinct().count()
                
                basic_facts_progress[subtopic_name].append({
                    'display_level': display_level,
                    'level_number': level_num,
                    'best_points': float(best_result.points),
                    'best_time_seconds': best_result.time_taken_seconds,
                    'best_date': best_result.completed_at,
                    'total_attempts': total_attempts
                })
            else:
                # Check session for old data (for migration/backward compatibility)
                results_key = f"basic_facts_results_{request.user.id}_{level_num}"
                results_list = request.session.get(results_key, [])
                
                if results_list:
                    # Migrate session data to database (one-time migration)
                    try:
                        for result_entry in results_list:
                            # Fix old format points if needed
                            points = result_entry.get('points', 0)
                            if points > 100:
                                points = points / 10
                            
                            # Check if this session_id already exists in DB
                            session_id = result_entry.get('session_id', '')
                            if session_id and not BasicFactsResult.objects.filter(
                                student=request.user,
                                level=level,
                                session_id=session_id
                            ).exists():
                                # Migrate to database
                                date_str = result_entry.get('date', '')
                                if isinstance(date_str, str):
                                    try:
                                        completed_date = datetime.fromisoformat(date_str)
                                    except:
                                        completed_date = datetime.now()
                                else:
                                    completed_date = date_str if date_str else datetime.now()
                                
                                BasicFactsResult.objects.create(
                                    student=request.user,
                                    level=level,
                                    session_id=session_id,
                                    score=result_entry.get('score', 0),
                                    total_points=result_entry.get('total_points', 10),
                                    time_taken_seconds=result_entry.get('time_taken_seconds', 0),
                                    points=points,
                                    completed_at=completed_date
                                )
                        
                        # After migration, get from database again
                        db_results = BasicFactsResult.objects.filter(
                            student=request.user,
                            level=level
                        ).order_by('-points')
                        
                        if db_results.exists():
                            best_result = db_results.first()
                            display_level = level_num
                            if 100 <= level_num <= 106:
                                display_level = level_num - 99
                            elif 107 <= level_num <= 113:
                                display_level = level_num - 106
                            elif 114 <= level_num <= 120:
                                display_level = level_num - 113
                            elif 121 <= level_num <= 127:
                                display_level = level_num - 120
                            elif 128 <= level_num <= 132:
                                display_level = level_num - 127
                            
                            total_attempts = db_results.values('session_id').distinct().count()
                            
                            basic_facts_progress[subtopic_name].append({
                                'display_level': display_level,
                                'level_number': level_num,
                                'best_points': float(best_result.points),
                                'best_time_seconds': best_result.time_taken_seconds,
                                'best_date': best_result.completed_at,
                                'total_attempts': total_attempts
                            })
                    except Exception as e:
                        # If migration fails, fall back to session display
                        pass
        
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
def user_profile(request):
    """User profile page for viewing and editing profile information"""
    user = request.user
    profile_form = UserProfileForm(instance=user)
    password_form = UserPasswordChangeForm(user=user)
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'update_profile':
            profile_form = UserProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect("maths:user_profile")
        
        elif action == 'change_password':
            password_form = UserPasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Password changed successfully!")
                return redirect("maths:user_profile")
    
    return render(request, "maths/user_profile.html", {
        "profile_form": profile_form,
        "password_form": password_form,
        "user": user
    })

def get_or_create_time_log(user):
    """Get or create TimeLog for user and handle resets"""
    time_log, created = TimeLog.objects.get_or_create(student=user)
    if created:
        # Initialize with current date/week
        from django.utils import timezone
        now = timezone.now()
        time_log.last_reset_date = now.date()
        time_log.last_reset_week = now.isocalendar()[1]
        time_log.save()
    else:
        # Check and reset if needed
        time_log.reset_daily_if_needed()
        time_log.reset_weekly_if_needed()
    return time_log

def update_time_log_from_activities(user):
    """Update TimeLog by summing time from all completed activities"""
    from django.utils import timezone
    from django.db.models import Sum
    from datetime import timedelta
    
    time_log = get_or_create_time_log(user)
    
    # Get today's date for filtering
    today = timezone.now().date()
    
    # Get current week (ISO week number)
    now = timezone.now()
    current_week = now.isocalendar()[1]
    
    # Sum time from StudentAnswer records (regular quizzes and measurements)
    # Only count completed sessions (where time_taken_seconds > 0)
    daily_student_answers = StudentAnswer.objects.filter(
        student=user,
        answered_at__date=today,
        time_taken_seconds__gt=0
    ).values('session_id', 'time_taken_seconds').distinct('session_id')
    
    # For daily: sum unique session times (each session represents one activity)
    daily_time_from_student_answers = 0
    seen_sessions = set()
    for answer in StudentAnswer.objects.filter(
        student=user,
        answered_at__date=today,
        time_taken_seconds__gt=0
    ).order_by('session_id', 'answered_at'):
        if answer.session_id and answer.session_id not in seen_sessions:
            seen_sessions.add(answer.session_id)
            daily_time_from_student_answers += answer.time_taken_seconds
    
    # For weekly: same logic but for current week
    weekly_time_from_student_answers = 0
    seen_weekly_sessions = set()
    # Get start of week (Monday)
    days_since_monday = now.weekday()
    week_start = now.date() - timedelta(days=days_since_monday)
    
    for answer in StudentAnswer.objects.filter(
        student=user,
        answered_at__date__gte=week_start,
        time_taken_seconds__gt=0
    ).order_by('session_id', 'answered_at'):
        if answer.session_id and answer.session_id not in seen_weekly_sessions:
            seen_weekly_sessions.add(answer.session_id)
            weekly_time_from_student_answers += answer.time_taken_seconds
    
    # Sum time from BasicFactsResult records
    daily_basic_facts = BasicFactsResult.objects.filter(
        student=user,
        completed_at__date=today
    ).values('session_id').annotate(
        session_time=Sum('time_taken_seconds')
    ).aggregate(total=Sum('time_taken_seconds'))['total'] or 0
    
    weekly_basic_facts = BasicFactsResult.objects.filter(
        student=user,
        completed_at__date__gte=week_start
    ).values('session_id').annotate(
        session_time=Sum('time_taken_seconds')
    ).aggregate(total=Sum('time_taken_seconds'))['total'] or 0
    
    # Update TimeLog with total time from activities
    time_log.daily_total_seconds = daily_time_from_student_answers + daily_basic_facts
    time_log.weekly_total_seconds = weekly_time_from_student_answers + weekly_basic_facts
    time_log.save(update_fields=['daily_total_seconds', 'weekly_total_seconds', 'last_activity'])
    
    return time_log

@login_required
@require_http_methods(["GET", "POST"])
def update_time_log(request):
    """AJAX endpoint to get current time log (calculated from activities)"""
    if not request.user.is_authenticated or request.user.is_teacher:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    try:
        # Recalculate time from activities
        time_log = update_time_log_from_activities(request.user)
        
        # Always return current time calculated from activities
        return JsonResponse({
            'success': True,
            'daily_seconds': time_log.daily_total_seconds,
            'weekly_seconds': time_log.weekly_total_seconds
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
            # With carry over (units digits sum >= 10)
            a = random.randint(15, 99)
            a_units = a % 10
            b_tens = random.randint(1, 8)
            # Need b_units such that a_units + b_units >= 10 (requires carry over)
            # b_units should be >= (10 - a_units) and <= 9
            min_b_units = max(1, 10 - a_units)
            max_b_units = 9
            if min_b_units <= max_b_units:
                b_units = random.randint(min_b_units, max_b_units)
            else:
                # If a_units is 0, we'd need b_units >= 10 which is impossible
                # Regenerate a so a_units > 0, or use fallback approach
                # Regenerate a to ensure a_units is not 0
                while a_units == 0:
                    a = random.randint(15, 99)
                    a_units = a % 10
                min_b_units = max(1, 10 - a_units)
                b_units = random.randint(min_b_units, 9)
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
            # Subtraction with borrowing (a_units < b_units)
            a = random.randint(10, 99)
            a_units = a % 10
            # b must be > a_units to require borrowing, but <= 9
            # If a_units is 9, there's no valid b (would need b > 9)
            # So we ensure a_units < 9, or adjust the range
            min_b = a_units + 1
            max_b = 9
            if min_b <= max_b:
                b = random.randint(min_b, max_b)
            else:
                # If a_units is 9, we can't create a borrowing scenario with single digits
                # So generate a new 'a' that allows borrowing, or use a fallback
                # Regenerate a with units digit < 9
                while a_units >= 9:
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
    
    elif 128 <= level_num <= 132:  # Place Value Facts
        target_values = {128: 10, 129: 100, 130: 1000, 131: 10000, 132: 100000}
        target = target_values.get(level_num)
        
        if target is None:
            return None, None
        
        # Randomly choose question format: 0 = a + b = ?, 1 = a + ? = target, 2 = ? + b = target
        question_type = random.randint(0, 2)
        
        if level_num == 128:  # Combinations for 10
            if question_type == 0:
                # a + b = ?
                a = random.randint(1, 9)
                b = target - a
                return f"{a} + {b} = ?", str(target)
            elif question_type == 1:
                # a + ? = 10
                a = random.randint(1, 9)
                b = target - a
                return f"{a} + ? = {target}", str(b)
            else:
                # ? + b = 10
                b = random.randint(1, 9)
                a = target - b
                return f"? + {b} = {target}", str(a)
        
        elif level_num == 129:  # Combinations for 100
            if question_type == 0:
                # a + b = ?
                # Can be simple (e.g., 40 + 60) or complex (e.g., 63 + 37)
                use_complex = random.choice([True, False])
                if use_complex:
                    # Generate numbers that add to 100 with varied digits
                    a = random.randint(10, 99)
                    b = target - a
                    if b < 10 or b > 99:
                        # Fallback to simple case
                        a = random.randint(10, 90)
                        b = target - a
                else:
                    # Simple case: multiples of 10
                    a_tens = random.randint(1, 9)
                    a = a_tens * 10
                    b = target - a
                return f"{a} + {b} = ?", str(target)
            elif question_type == 1:
                # a + ? = 100
                a = random.randint(10, 99)
                b = target - a
                return f"{a} + ? = {target}", str(b)
            else:
                # ? + b = 100
                b = random.randint(10, 99)
                a = target - b
                return f"? + {b} = {target}", str(a)
        
        elif level_num == 130:  # Combinations for 1000
            if question_type == 0:
                # a + b = ?
                a = random.randint(100, 999)
                b = target - a
                return f"{a} + {b} = ?", str(target)
            elif question_type == 1:
                # a + ? = 1000
                a = random.randint(100, 999)
                b = target - a
                return f"{a} + ? = {target}", str(b)
            else:
                # ? + b = 1000
                b = random.randint(100, 999)
                a = target - b
                return f"? + {b} = {target}", str(a)
        
        elif level_num == 131:  # Combinations for 10000
            if question_type == 0:
                # a + b = ?
                a = random.randint(1000, 9999)
                b = target - a
                return f"{a} + {b} = ?", str(target)
            elif question_type == 1:
                # a + ? = 10000
                a = random.randint(1000, 9999)
                b = target - a
                return f"{a} + ? = {target}", str(b)
            else:
                # ? + b = 10000
                b = random.randint(1000, 9999)
                a = target - b
                return f"? + {b} = {target}", str(a)
        
        elif level_num == 132:  # Combinations for 100000
            if question_type == 0:
                # a + b = ?
                a = random.randint(10000, 99999)
                b = target - a
                return f"{a} + {b} = ?", str(target)
            elif question_type == 1:
                # a + ? = 100000
                a = random.randint(10000, 99999)
                b = target - a
                return f"{a} + ? = {target}", str(b)
            else:
                # ? + b = 100000
                b = random.randint(10000, 99999)
                a = target - b
                return f"? + {b} = {target}", str(a)
    
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
    valid_subtopics = ['Addition', 'Subtraction', 'Multiplication', 'Division', 'Place Value Facts']
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
        'Division': '➗',
        'Place Value Facts': '🔢'
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
        
        # Store question/answer review data for Basic Facts popup
        question_review_data = [] if is_basic_facts else None
        
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
                
                # Store question/answer data for review popup
                question_review_data.append({
                    'question_text': question.question_text,
                    'student_answer': student_answer,
                    'correct_answer': question.correct_answer,
                    'is_correct': is_correct,
                    'points': question.points if is_correct else 0
                })
                
                # For Basic Facts, results are stored in database after quiz completion
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
        
        # For Basic Facts, store results in database for persistent tracking
        if is_basic_facts:
            # Calculate points same as measurements, but divide by 10 for Basic Facts
            percentage = (score / total_points) if total_points else 0
            final_points_calc = ((percentage * 100 * 60) / time_taken_seconds) / 10 if time_taken_seconds else 0
            final_points_calc = round(final_points_calc, 2)
            
            # Save to database
            BasicFactsResult.objects.create(
                student=request.user,
                level=level,
                session_id=session_id,
                score=score,
                total_points=total_points,
                time_taken_seconds=time_taken_seconds,
                points=final_points_calc
            )
            
            # Update time log from activities
            if not request.user.is_teacher:
                update_time_log_from_activities(request.user)
            
            # Also keep in session for backward compatibility (optional)
            basic_facts_results_key = f"basic_facts_results_{request.user.id}_{level_number}"
            results_list = request.session.get(basic_facts_results_key, [])
            result_entry = {
                'session_id': session_id,
                'score': score,
                'total_points': total_points,
                'time_taken_seconds': time_taken_seconds,
                'points': final_points_calc,
                'date': datetime.now().isoformat()
            }
            results_list.append(result_entry)
            request.session[basic_facts_results_key] = results_list
            
            # Clear questions from session
            if session_questions_key in request.session:
                del request.session[session_questions_key]
        
        # Clear timer from session
        if timer_session_key in request.session:
            del request.session[timer_session_key]
        
        # Update time log from activities (for both Basic Facts and regular quizzes)
        if not request.user.is_teacher:
            update_time_log_from_activities(request.user)
        
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
            # For Basic Facts, check database for previous results (excluding current session)
            previous_results = BasicFactsResult.objects.filter(
                student=request.user,
                level=level
            ).exclude(session_id=session_id).order_by('-points')
            
            if previous_results.exists():
                previous_best_points = float(previous_results.first().points)
            else:
                previous_best_points = None
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
                "is_first_attempt": is_first_attempt,
                "question_review_data": question_review_data,
                "is_basic_facts": True
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
    # Filter to only include measurement questions and exclude Place Values questions
    all_questions_query = Question.objects.filter(level=level).filter(
        Q(question_text__icontains='measure') |
        Q(question_text__icontains='length') |
        Q(question_text__icontains='width') |
        Q(question_text__icontains='height') |
        Q(question_text__icontains='centimeter') |
        Q(question_text__icontains='meter') |
        Q(question_text__icontains='kilometer') |
        Q(question_text__icontains='liter') |
        Q(question_text__icontains='gram') |
        Q(question_text__icontains='kilogram') |
        Q(question_text__icontains='unit would you use') |
        Q(question_text__icontains='ruler') |
        Q(question_text__icontains='scale')
    ).exclude(
        Q(question_text__icontains='complete the following sequence') |
        Q(question_text__icontains='counting on') |
        Q(question_text__icontains='counting back') |
        Q(question_text__icontains='skip counting') |
        Q(question_text__icontains='tens and ones') |
        Q(question_text__icontains='How many tens')
    )
    
    # Question limits per year
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    question_limit = YEAR_QUESTION_COUNTS.get(level.level_number, 10)
    
    # Get current question number from URL parameter (default to 1)
    question_number = int(request.GET.get('q', 1))
    
    # Start timer on first question load and create session
    timer_session_key = "measurements_timer_start"
    questions_session_key = "measurements_question_ids"
    timer_start = request.session.get(timer_session_key)
    
    # Clear session if questions don't match Measurements patterns (safety check)
    if question_number == 1 and timer_start:
        # Validate existing session questions are still Measurements questions
        existing_question_ids = request.session.get(questions_session_key, [])
        if existing_question_ids:
            existing_questions = Question.objects.filter(id__in=existing_question_ids, level=level)
            # Check if any question doesn't match Measurements pattern
            invalid_questions = existing_questions.exclude(
                Q(question_text__icontains='measure') |
                Q(question_text__icontains='length') |
                Q(question_text__icontains='width') |
                Q(question_text__icontains='height') |
                Q(question_text__icontains='centimeter') |
                Q(question_text__icontains='meter') |
                Q(question_text__icontains='kilometer') |
                Q(question_text__icontains='unit would you use')
            ).filter(
                Q(question_text__icontains='complete the following sequence') |
                Q(question_text__icontains='counting on') |
                Q(question_text__icontains='counting back') |
                Q(question_text__icontains='skip counting') |
                Q(question_text__icontains='tens and ones') |
                Q(question_text__icontains='How many tens')
            )
            if invalid_questions.exists():
                # Clear session and start fresh
                if timer_session_key in request.session:
                    del request.session[timer_session_key]
                if questions_session_key in request.session:
                    del request.session[questions_session_key]
                if 'current_attempt_id' in request.session:
                    del request.session['current_attempt_id']
                timer_start = None
    
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
    
    # Convert to list and maintain the order from session
    # Validate that all questions are Measurements questions
    if question_ids:
        all_questions = []
        for qid in question_ids:
            try:
                question = Question.objects.get(id=qid, level=level)
                # Verify this is a Measurements question
                is_measurement = (
                    'measure' in question.question_text.lower() or
                    'length' in question.question_text.lower() or
                    'width' in question.question_text.lower() or
                    'height' in question.question_text.lower() or
                    'centimeter' in question.question_text.lower() or
                    'meter' in question.question_text.lower() or
                    'kilometer' in question.question_text.lower() or
                    'liter' in question.question_text.lower() or
                    'unit would you use' in question.question_text.lower()
                )
                # Exclude Place Values questions
                is_place_value = (
                    'complete the following sequence' in question.question_text.lower() or
                    'counting on' in question.question_text.lower() or
                    'counting back' in question.question_text.lower() or
                    'skip counting' in question.question_text.lower() or
                    'tens and ones' in question.question_text.lower() or
                    'how many tens' in question.question_text.lower()
                )
                if is_measurement and not is_place_value:
                    all_questions.append(question)
            except Question.DoesNotExist:
                continue
        
        # If we filtered out questions, clear session and start fresh
        if len(all_questions) != len(question_ids):
            if timer_session_key in request.session:
                del request.session[timer_session_key]
            if questions_session_key in request.session:
                del request.session[questions_session_key]
            if 'current_attempt_id' in request.session:
                del request.session['current_attempt_id']
            # Redirect to question 1 with fresh questions
            return redirect(f"{request.path}?q=1")
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
        
        # Update time log from activities
        if not request.user.is_teacher:
            update_time_log_from_activities(request.user)
        
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

@login_required
def place_values_questions(request, level_number):
    """Show Place Values questions one by one"""
    level = get_object_or_404(Level, level_number=level_number)
    
    # Check if student has access to this level
    allowed = student_allowed_levels(request.user)
    if allowed is not None and not allowed.filter(pk=level.pk).exists():
        messages.error(request, "You don't have access to this level.")
        return redirect("maths:dashboard")
    
    # Get Place Values topic
    place_values_topic = Topic.objects.filter(name="Place Values").first()
    if not place_values_topic:
        messages.error(request, "Place Values topic not found.")
        return redirect("maths:dashboard")
    
    # Get all Place Values questions for this level
    # Filter to only include Place Values questions by matching their specific patterns
    # Place Values questions contain: "complete the following sequence", "counting", "tens and ones", "skip counting"
    # Also exclude measurement questions explicitly
    all_questions_query = Question.objects.filter(level=level).filter(
        Q(question_text__icontains='complete the following sequence') |
        Q(question_text__icontains='counting on') |
        Q(question_text__icontains='counting back') |
        Q(question_text__icontains='skip counting') |
        Q(question_text__icontains='tens and ones') |
        Q(question_text__icontains='How many tens')
    ).exclude(
        Q(question_text__icontains='Which unit would you use') |
        Q(question_text__icontains='measure the length') |
        Q(question_text__icontains='measure the width') |
        Q(question_text__icontains='measure the height') |
        Q(question_text__icontains='centimeter') |
        Q(question_text__icontains='meter') |
        Q(question_text__icontains='kilometer') |
        Q(question_text__icontains='liter') |
        Q(question_text__icontains='gram')
    )
    
    # Question limits per year
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    question_limit = YEAR_QUESTION_COUNTS.get(level.level_number, 10)
    
    # Get current question number from URL parameter (default to 1)
    question_number = int(request.GET.get('q', 1))
    
    # Start timer on first question load and create session
    timer_session_key = "place_values_timer_start"
    questions_session_key = "place_values_question_ids"
    timer_start = request.session.get(timer_session_key)
    
    # Clear session if questions don't match Place Values patterns (safety check)
    if question_number == 1 and timer_start:
        # Validate existing session questions are still Place Values questions
        existing_question_ids = request.session.get(questions_session_key, [])
        if existing_question_ids:
            existing_questions = Question.objects.filter(id__in=existing_question_ids, level=level)
            # Check if any question doesn't match Place Values pattern
            invalid_questions = existing_questions.exclude(
                Q(question_text__icontains='complete the following sequence') |
                Q(question_text__icontains='counting on') |
                Q(question_text__icontains='counting back') |
                Q(question_text__icontains='skip counting') |
                Q(question_text__icontains='tens and ones') |
                Q(question_text__icontains='How many tens')
            )
            if invalid_questions.exists():
                # Clear session and start fresh
                if timer_session_key in request.session:
                    del request.session[timer_session_key]
                if questions_session_key in request.session:
                    del request.session[questions_session_key]
                if 'current_attempt_id' in request.session:
                    del request.session['current_attempt_id']
                timer_start = None
    
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
    
    # Convert to list and maintain the order from session
    # Validate that all questions are Place Values questions
    if question_ids:
        all_questions = []
        for qid in question_ids:
            try:
                question = Question.objects.get(id=qid, level=level)
                # Verify this is a Place Values question
                is_place_value = (
                    'complete the following sequence' in question.question_text.lower() or
                    'counting on' in question.question_text.lower() or
                    'counting back' in question.question_text.lower() or
                    'skip counting' in question.question_text.lower() or
                    'tens and ones' in question.question_text.lower() or
                    'how many tens' in question.question_text.lower()
                )
                # Exclude measurement questions
                is_measurement = (
                    'which unit would you use' in question.question_text.lower() or
                    'measure the length' in question.question_text.lower() or
                    'measure the width' in question.question_text.lower() or
                    'centimeter' in question.question_text.lower() or
                    'meter' in question.question_text.lower() or
                    'kilometer' in question.question_text.lower() or
                    'liter' in question.question_text.lower()
                )
                if is_place_value and not is_measurement:
                    all_questions.append(question)
            except Question.DoesNotExist:
                continue
        
        # If we filtered out questions, clear session and start fresh
        if len(all_questions) != len(question_ids):
            if timer_session_key in request.session:
                del request.session[timer_session_key]
            if questions_session_key in request.session:
                del request.session[questions_session_key]
            if 'current_attempt_id' in request.session:
                del request.session['current_attempt_id']
            # Redirect to question 1 with fresh questions
            return redirect(f"{request.path}?q=1")
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
                        # Short answer question
                        attempt_id = request.session.get('current_attempt_id', '')
                        student_answer, created = StudentAnswer.objects.update_or_create(
                            student=request.user,
                            question=question,
                            defaults={
                                'text_answer': text_answer,
                                'is_correct': True,  # For demo purposes, always correct
                                'points_earned': question.points,
                                'session_id': attempt_id
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
        
        # Update time log from activities
        if not request.user.is_teacher:
            update_time_log_from_activities(request.user)
        
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
            "topic": place_values_topic,
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
        "topic": place_values_topic,
        "student_answers": student_answers,
        "checked": checked,
        "selected_answer": selected_answer,
        "is_text_answer": is_text_answer,
        "is_last_question": question_number == len(all_questions),
        "elapsed_seconds": elapsed_seconds
    })

@login_required
def fractions_questions(request, level_number):
    """Show Fractions questions one by one"""
    level = get_object_or_404(Level, level_number=level_number)
    
    # Check if student has access to this level
    allowed = student_allowed_levels(request.user)
    if allowed is not None and not allowed.filter(pk=level.pk).exists():
        messages.error(request, "You don't have access to this level.")
        return redirect("maths:dashboard")
    
    # Get Fractions topic
    fractions_topic = Topic.objects.filter(name="Fractions").first()
    if not fractions_topic:
        messages.error(request, "Fractions topic not found.")
        return redirect("maths:dashboard")
    
    # Get all Fractions questions for this level
    # Filter to only include Fractions questions (numerator, denominator)
    all_questions_query = Question.objects.filter(level=level).filter(
        Q(question_text__icontains='numerator') |
        Q(question_text__icontains='denominator') |
        Q(question_text__icontains='fraction')
    )
    
    # Question limits per year
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    question_limit = YEAR_QUESTION_COUNTS.get(level.level_number, 10)
    
    # Get current question number from URL parameter (default to 1)
    question_number = int(request.GET.get('q', 1))
    
    # Start timer on first question load and create session
    timer_session_key = "fractions_timer_start"
    questions_session_key = "fractions_question_ids"
    timer_start = request.session.get(timer_session_key)
    
    # Clear session if questions don't match Fractions patterns (safety check)
    if question_number == 1 and timer_start:
        # Validate existing session questions are still Fractions questions
        existing_question_ids = request.session.get(questions_session_key, [])
        if existing_question_ids:
            existing_questions = Question.objects.filter(id__in=existing_question_ids, level=level)
            # Check if any question doesn't match Fractions pattern
            invalid_questions = existing_questions.exclude(
                Q(question_text__icontains='numerator') |
                Q(question_text__icontains='denominator') |
                Q(question_text__icontains='fraction')
            )
            if invalid_questions.exists():
                # Clear session and start fresh
                if timer_session_key in request.session:
                    del request.session[timer_session_key]
                if questions_session_key in request.session:
                    del request.session[questions_session_key]
                if 'current_attempt_id' in request.session:
                    del request.session['current_attempt_id']
                timer_start = None
    
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
    
    # Convert to list and maintain the order from session
    # Validate that all questions are Fractions questions
    if question_ids:
        all_questions = []
        for qid in question_ids:
            try:
                question = Question.objects.get(id=qid, level=level)
                # Verify this is a Fractions question
                is_fraction = (
                    'numerator' in question.question_text.lower() or
                    'denominator' in question.question_text.lower() or
                    'fraction' in question.question_text.lower()
                )
                if is_fraction:
                    all_questions.append(question)
            except Question.DoesNotExist:
                continue
        
        # If we filtered out questions, clear session and start fresh
        if len(all_questions) != len(question_ids):
            if timer_session_key in request.session:
                del request.session[timer_session_key]
            if questions_session_key in request.session:
                del request.session[questions_session_key]
            if 'current_attempt_id' in request.session:
                del request.session['current_attempt_id']
            # Redirect to question 1 with fresh questions
            return redirect(f"{request.path}?q=1")
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
                        # Short answer question
                        attempt_id = request.session.get('current_attempt_id', '')
                        student_answer, created = StudentAnswer.objects.update_or_create(
                            student=request.user,
                            question=question,
                            defaults={
                                'text_answer': text_answer,
                                'is_correct': True,  # For demo purposes, always correct
                                'points_earned': question.points,
                                'session_id': attempt_id
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
        
        # Update time log from activities
        if not request.user.is_teacher:
            update_time_log_from_activities(request.user)
        
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
            "topic": fractions_topic,
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
        "topic": fractions_topic,
        "student_answers": student_answers,
        "checked": checked,
        "selected_answer": selected_answer,
        "is_text_answer": is_text_answer,
        "is_last_question": question_number == len(all_questions),
        "elapsed_seconds": elapsed_seconds
    })

@login_required
def bodmas_questions(request, level_number):
    """Show BODMAS/PEMDAS questions one by one - similar to fractions_questions"""
    # Import the fractions_questions view logic but filter for BODMAS questions
    level = get_object_or_404(Level, level_number=level_number)
    
    # Check if student has access to this level
    allowed = student_allowed_levels(request.user)
    if allowed is not None and not allowed.filter(pk=level.pk).exists():
        messages.error(request, "You don't have access to this level.")
        return redirect("maths:dashboard")
    
    # Get BODMAS/PEMDAS topic
    bodmas_topic = Topic.objects.filter(name="BODMAS/PEMDAS").first()
    if not bodmas_topic:
        messages.error(request, "BODMAS/PEMDAS topic not found.")
        return redirect("maths:dashboard")
    
    # Get all BODMAS/PEMDAS questions for this level
    # Filter by level and topic directly - much simpler!
    all_questions_query = Question.objects.filter(
        level=level,
        topic=bodmas_topic
    )
    
    # Question limits per year
    YEAR_QUESTION_COUNTS = {2: 10, 3: 12, 4: 15, 5: 17, 6: 20, 7: 22, 8: 25, 9: 30}
    question_limit = YEAR_QUESTION_COUNTS.get(level.level_number, 10)
    
    # Get current question number from URL parameter (default to 1)
    question_number = int(request.GET.get('q', 1))
    
    # Start timer on first question load and create session
    timer_session_key = "bodmas_timer_start"
    questions_session_key = "bodmas_question_ids"
    timer_start = request.session.get(timer_session_key)
    
    # Clear session if questions don't belong to BODMAS topic (safety check)
    if question_number == 1 and timer_start:
        existing_question_ids = request.session.get(questions_session_key, [])
        if existing_question_ids:
            # Check if questions belong to BODMAS topic
            invalid_questions = Question.objects.filter(
                id__in=existing_question_ids,
                level=level
            ).exclude(topic=bodmas_topic)
            
            if invalid_questions.exists():
                if timer_session_key in request.session:
                    del request.session[timer_session_key]
                if questions_session_key in request.session:
                    del request.session[questions_session_key]
                if 'current_attempt_id' in request.session:
                    del request.session['current_attempt_id']
                timer_start = None
    
    if question_number == 1 and not timer_start:
        request.session[timer_session_key] = time.time()
        import uuid
        request.session['current_attempt_id'] = str(uuid.uuid4())
        
        all_questions_list = list(all_questions_query)
        if len(all_questions_list) > question_limit:
            selected_questions = random.sample(all_questions_list, question_limit)
        else:
            selected_questions = all_questions_list
        
        random.shuffle(selected_questions)
        request.session[questions_session_key] = [q.id for q in selected_questions]
    
    question_ids = request.session.get(questions_session_key, [])
    
    if question_ids:
        all_questions = []
        for qid in question_ids:
            try:
                question = Question.objects.get(id=qid, level=level)
                # Check if it's a BODMAS question using strict whitelist
                q_text_lower = question.question_text.lower()
                is_bodmas = (
                    q_text_lower.startswith('evaluate:') or
                    q_text_lower.startswith('calculate:') or
                    q_text_lower.startswith('find the missing number:') or
                    q_text_lower.startswith('i think of a number') or
                    q_text_lower.startswith('i add') or
                    q_text_lower.startswith('i multiply') or
                    q_text_lower.startswith('using the digits') or
                    q_text_lower.startswith('write down what') or
                    'bodmas' in q_text_lower or
                    'pemdas' in q_text_lower or
                    'bidmas' in q_text_lower or
                    '_____' in question.question_text  # Missing number pattern
                )
                # Exclude measurement, fraction, and place value questions
                is_not_bodmas = (
                    'cm' in q_text_lower or
                    'centimeter' in q_text_lower or
                    'meter' in q_text_lower or
                    'kilometer' in q_text_lower or
                    'liter' in q_text_lower or
                    'gram' in q_text_lower or
                    'kilogram' in q_text_lower or
                    'width' in q_text_lower or
                    'height' in q_text_lower or
                    'length' in q_text_lower or
                    'area' in q_text_lower or
                    'perimeter' in q_text_lower or
                    'volume' in q_text_lower or
                    'measure' in q_text_lower or
                    'unit would you use' in q_text_lower or
                    'ruler' in q_text_lower or
                    'scale' in q_text_lower or
                    'numerator' in q_text_lower or
                    'denominator' in q_text_lower or
                    'fraction' in q_text_lower or
                    'complete the following sequence' in q_text_lower or
                    'counting on' in q_text_lower or
                    'counting back' in q_text_lower or
                    'skip counting' in q_text_lower or
                    'tens and ones' in q_text_lower or
                    'how many tens' in q_text_lower
                )
                if is_bodmas and not is_not_bodmas:
                    all_questions.append(question)
            except Question.DoesNotExist:
                continue
        
        if len(all_questions) != len(question_ids):
            if timer_session_key in request.session:
                del request.session[timer_session_key]
            if questions_session_key in request.session:
                del request.session[questions_session_key]
            if 'current_attempt_id' in request.session:
                del request.session['current_attempt_id']
            return redirect(f"{request.path}?q=1")
    else:
        # No session exists - initialize it now
        if not timer_start:
            request.session[timer_session_key] = time.time()
            import uuid
            request.session['current_attempt_id'] = str(uuid.uuid4())
        
        all_questions_list = list(all_questions_query)
        if len(all_questions_list) > question_limit:
            selected_questions = random.sample(all_questions_list, question_limit)
        else:
            selected_questions = all_questions_list
        
        random.shuffle(selected_questions)
        request.session[questions_session_key] = [q.id for q in selected_questions]
        all_questions = selected_questions
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'check_answer':
            question_id = request.POST.get('question_id')
            answer_id = request.POST.get('answer_id')
            text_answer = request.POST.get('text_answer')
            
            if question_id:
                try:
                    question = Question.objects.get(id=question_id, level=level, topic=bodmas_topic)
                    
                    if answer_id:
                        answer = Answer.objects.get(id=answer_id, question=question)
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
                        return redirect(f"{request.path}?q={question_number}&checked=1&answer_id={answer_id}")
                    
                    elif text_answer and question.question_type == 'short_answer':
                        attempt_id = request.session.get('current_attempt_id', '')
                        student_answer, created = StudentAnswer.objects.update_or_create(
                            student=request.user,
                            question=question,
                            defaults={
                                'text_answer': text_answer,
                                'is_correct': True,
                                'points_earned': question.points,
                                'session_id': attempt_id
                            }
                        )
                        return redirect(f"{request.path}?q={question_number}&checked=1&text_answer={text_answer}")
                    
                except (Question.DoesNotExist, Answer.DoesNotExist):
                    messages.error(request, "Invalid question or answer.")
        
        elif action == 'next_question':
            next_question = question_number + 1
            if next_question <= len(all_questions):
                return redirect(f"{request.path}?q={next_question}")
            else:
                return redirect(f"{request.path}?completed=1")
    
    completed = request.GET.get('completed') == '1'
    
    if completed:
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
        
        student_answers.update(time_taken_seconds=total_time_seconds)
        
        if not request.user.is_teacher:
            update_time_log_from_activities(request.user)
        
        if timer_session_key in request.session:
            del request.session[timer_session_key]
        if questions_session_key in request.session:
            del request.session[questions_session_key]
        if 'current_attempt_id' in request.session:
            del request.session['current_attempt_id']
        
        return render(request, 'maths/measurements_questions.html', {
            'level': level,
            'topic': bodmas_topic,
            'completed': True,
            'total_score': total_score,
            'total_points': total_points,
            'total_questions': len(all_questions),
            'total_time_seconds': total_time_seconds,
            'correct_count': sum(1 for answer in student_answers if answer.is_correct)
        })
    
    if not all_questions or question_number > len(all_questions):
        messages.error(request, "Invalid question number.")
        return redirect("maths:dashboard")
    
    current_question = all_questions[question_number - 1]
    answers = current_question.answers.all()
    
    checked = request.GET.get('checked') == '1'
    answer_id = request.GET.get('answer_id')
    text_answer = request.GET.get('text_answer')
    selected_answer = None
    is_text_answer = False
    
    if checked:
        if answer_id:
            try:
                selected_answer = Answer.objects.get(id=answer_id, question=current_question)
            except Answer.DoesNotExist:
                pass
        elif text_answer:
            is_text_answer = True
            selected_answer = text_answer
    
    if timer_start:
        elapsed_seconds = int(time.time() - timer_start)
    else:
        elapsed_seconds = 0
    
    return render(request, 'maths/measurements_questions.html', {
        'level': level,
        'topic': bodmas_topic,
        'current_question': current_question,
        'answers': answers,
        'question_number': question_number,
        'total_questions': len(all_questions),
        'checked': checked,
        'selected_answer': selected_answer,
        'is_text_answer': is_text_answer,
        "is_last_question": question_number == len(all_questions),
        "elapsed_seconds": elapsed_seconds
    })

