from django import template
from django.utils.text import slugify

register = template.Library()

@register.filter
def underscore_slugify(value):
    return slugify(value).replace('-', '_').lower()


@register.filter
def get_meal(plan, meal_type):
    """Retrieve meal name from the plan dictionary."""
    if isinstance(plan, dict):
        return plan.get(meal_type, None)
    return None

@register.filter
def split(value, sep=','):
    return value.split(sep)