from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ClassRoom, Question, Answer

class TeacherSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username","email","password1","password2")
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        return user

class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username","email","password1","password2")
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = False
        if commit:
            user.save()
        return user

class CreateClassForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ("name", "levels")

class TeacherCenterRegistrationForm(UserCreationForm):
    center_name = forms.CharField(max_length=150, label="Center/School Name")
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "center_name")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        return user

class IndividualStudentRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = False
        if commit:
            user.save()
        return user

class StudentBulkRegistrationForm(forms.Form):
    student_data = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 50}),
        help_text="Enter student information in the format: username,email,password (one per line)"
    )
    
    def clean_student_data(self):
        data = self.cleaned_data['student_data']
        lines = data.strip().split('\n')
        students = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            parts = line.split(',')
            if len(parts) != 3:
                raise forms.ValidationError(f"Line {i}: Invalid format. Expected 'username,email,password'")
            
            username, email, password = [part.strip() for part in parts]
            
            # Validate username
            if not username:
                raise forms.ValidationError(f"Line {i}: Username cannot be empty")
            
            # Validate email
            if '@' not in email:
                raise forms.ValidationError(f"Line {i}: Invalid email format")
            
            # Validate password
            if len(password) < 8:
                raise forms.ValidationError(f"Line {i}: Password must be at least 8 characters")
            
            students.append({
                'username': username,
                'email': email,
                'password': password
            })
        
        return students

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type', 'difficulty', 'points', 'explanation']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
            'explanation': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['answer_text', 'is_correct', 'order']
        widgets = {
            'answer_text': forms.TextInput(attrs={'size': 40}),
        }

class AnswerFormSet(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default values for answer forms
        for form in self.forms:
            if not form.instance.pk:  # New form
                form.fields['order'].initial = len(self.forms)

AnswerFormSet = forms.formset_factory(AnswerForm, extra=4, formset=AnswerFormSet)
