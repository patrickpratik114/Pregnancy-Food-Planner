from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'trimester', 'food_habits')  # Fields to display in the admin list view
    search_fields = ('user__username', 'age', 'trimester', 'food_habits')  # Fields to enable search
    list_filter = ('age', 'trimester', 'food_habits')  # Filters for the admin sidebar
    ordering = ('user',)  # Default ordering


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('age', 'trimester', 'allergy', 'genetic_condition', 'food_habits')  # Fields to display
    readonly_fields = ('age',)  # Example of making a field read-only


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

    # Add Profile fields to User list display
    def age(self, obj):
        return obj.profile.age

    def trimester(self, obj):
        return obj.profile.trimester

    def food_habits(self, obj):
        return obj.profile.food_habits

    age.short_description = 'Age'
    trimester.short_description = 'Trimester'
    food_habits.short_description = 'Food Habits'

    list_display = UserAdmin.list_display + ('age', 'trimester', 'food_habits')

    # Automatically create Profile when a User is created
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not hasattr(obj, 'profile'):
            Profile.objects.create(user=obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
