"""
Task Tracker Admin Configuration

This module configures the Django admin interface for the Task model.
"""

from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin configuration for Task model."""

    list_display = [
        'id',
        'title',
        'status',
        'priority',
        'due_date',
        'user',
        'created_at',
        'is_overdue',
    ]
    list_filter = [
        'status',
        'priority',
        'created_at',
        'due_date',
    ]
    search_fields = [
        'title',
        'description',
        'user__username',
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'due_date')
        }),
        ('Ownership', {
            'fields': ('user',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def is_overdue(self, obj):
        """Display overdue status."""
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'
