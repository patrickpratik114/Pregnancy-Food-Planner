from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    
    TRIMESTER_CHOICES = [
        ('1', 'First'),
        ('2', 'Second'),
        ('3', 'Third'),
    ]
    FOOD_HABITS_CHOICES = [
        ('vegetarian', 'Vegetarian'),
        ('non-vegetarian', 'Non-Vegetarian'),
        ('vegan', 'Vegan'),
        ('pescatarian', 'Pescatarian'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(blank=True, null=True)
    trimester = models.CharField(max_length=10)
    food_habits = models.CharField(max_length=100)

    allergy = models.JSONField(blank=True, null=True)
    genetic_condition = models.JSONField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.age}"
    

    def get_age_range(self):
        """Returns the min and max age for filtering meals."""
        if 18 <= self.age <= 25:
            return (18, 25)
        elif 26 <= self.age <= 35:
            return (26, 35)
        elif 36 <= self.age <= 45:
            return (36, 45)
        else:
            return (46, 100)

    def get_meal_filter_criteria(self):
        """Returns dictionary criteria for meal filtering."""
        min_age, max_age = self.get_age_range()
        return {
            "food_habit": self.food_habits,
            "allergy__overlap": self.allergy or [],
            "genetic_condition__overlap": self.genetic_condition or [],
            "trimester": self.trimester,
            "age__gte": min_age,
            "age__lte": max_age,
        }

class Meals(models.Model):
    id = models.AutoField(primary_key=True)
    Recipe = models.CharField(max_length=255, null=True)
    Food_Habit = models.CharField(max_length=50, null=True)
    Allergy = models.CharField(max_length=100, null=True)
    Genetic_Condition = models.CharField(max_length=100, null=True)
    age = models.IntegerField(null=True)
    Trimester = models.IntegerField(null=True)
    Meal_Type = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = 'meals'
        managed = False  # Tells Django not to manage this table's creation

    def __str__(self):
        return f"{self.Meal_Type} - {self.Recipe}"



class PregnancyDietaryNeeds(models.Model):
    recipe = models.TextField(db_column='Recipe', blank=True, null=True)  # Field name made lowercase.
    calories = models.IntegerField(db_column='Calories', blank=True, null=True)  # Field name made lowercase.
    protein = models.FloatField(db_column='Protein', blank=True, null=True)  # Field name made lowercase.
    vitamin_b9 = models.IntegerField(db_column='Vitamin_B9', blank=True, null=True)  # Field name made lowercase.
    vitamin_d = models.IntegerField(db_column='Vitamin_D', blank=True, null=True)  # Field name made lowercase.
    vitamin_a = models.IntegerField(db_column='Vitamin_A', blank=True, null=True)  # Field name made lowercase.
    iron = models.FloatField(db_column='Iron', blank=True, null=True)  # Field name made lowercase.
    calcium = models.IntegerField(db_column='Calcium', blank=True, null=True)  # Field name made lowercase.
    omega_3 = models.FloatField(db_column='Omega_3', blank=True, null=True)  # Field name made lowercase.
    iodine = models.IntegerField(db_column='Iodine', blank=True, null=True)  # Field name made lowercase.
    trimester = models.TextField(db_column='Trimester', blank=True, null=True)  # Field name made lowercase.
    genetic_condition = models.TextField(db_column='Genetic_Condition', blank=True, null=True)  # Field name made lowercase.
    allergy = models.TextField(db_column='Allergy', blank=True, null=True)  # Field name made lowercase.
    food_habit = models.TextField(db_column='Food_Habit', blank=True, null=True)  # Field name made lowercase.
    activity_level = models.TextField(db_column='Activity_Level', blank=True, null=True)  # Field name made lowercase.
    age = models.IntegerField(db_column='Age', blank=True, null=True)  # Field name made lowercase.
    height = models.IntegerField(db_column='Height', blank=True, null=True)  # Field name made lowercase.
    weight = models.IntegerField(db_column='Weight', blank=True, null=True)  # Field name made lowercase.
    ingredients = models.TextField(db_column='Ingredients', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pregnancy_dietary_needs'
        
        
class MealPlan(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.JSONField(default=dict)
    
    def clear_day(self, day):
        """Remove a specific day's meals from the plan."""
        if day in self.plan:
            del self.plan[day]
            self.save()