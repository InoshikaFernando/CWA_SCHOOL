from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Topic, Level, ClassRoom, Enrollment

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (*UserAdmin.fieldsets, ("Role", {"fields": ("is_teacher",)}))
    list_display = ("username", "email", "is_staff", "is_teacher")

admin.site.register(Topic)
admin.site.register(Level)
admin.site.register(ClassRoom)
admin.site.register(Enrollment)
