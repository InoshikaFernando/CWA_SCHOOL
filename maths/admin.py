from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Topic, Level, ClassRoom, Enrollment, BasicFactsResult

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (*UserAdmin.fieldsets, ("Role", {"fields": ("is_teacher",)}))
    list_display = ("username", "email", "is_staff", "is_teacher")

@admin.register(BasicFactsResult)
class BasicFactsResultAdmin(admin.ModelAdmin):
    list_display = ("student", "level", "points", "score", "total_points", "time_taken_seconds", "completed_at")
    list_filter = ("level", "completed_at")
    search_fields = ("student__username", "level__level_number")
    readonly_fields = ("completed_at",)
    ordering = ("-completed_at",)

admin.site.register(Topic)
admin.site.register(Level)
admin.site.register(ClassRoom)
admin.site.register(Enrollment)
