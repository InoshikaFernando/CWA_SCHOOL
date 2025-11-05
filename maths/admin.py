from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Topic, Level, ClassRoom, Enrollment, BasicFactsResult, TimeLog

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        ("Personal Information", {"fields": ("date_of_birth", "country", "region")}),
        ("Role", {"fields": ("is_teacher",)})
    )
    list_display = ("username", "email", "is_staff", "is_teacher", "country", "region")

@admin.register(BasicFactsResult)
class BasicFactsResultAdmin(admin.ModelAdmin):
    list_display = ("student", "level", "points", "score", "total_points", "time_taken_seconds", "completed_at")
    list_filter = ("level", "completed_at")
    search_fields = ("student__username", "level__level_number")
    readonly_fields = ("completed_at",)
    ordering = ("-completed_at",)

@admin.register(TimeLog)
class TimeLogAdmin(admin.ModelAdmin):
    list_display = ("student", "daily_total_seconds", "weekly_total_seconds", "last_reset_date", "last_activity")
    list_filter = ("last_reset_date", "last_activity")
    search_fields = ("student__username",)
    readonly_fields = ("last_reset_date", "last_activity")

admin.site.register(Topic)
admin.site.register(Level)
admin.site.register(ClassRoom)
admin.site.register(Enrollment)
