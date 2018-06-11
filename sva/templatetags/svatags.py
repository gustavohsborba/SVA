from django import template
from django.contrib.auth.models import Group

register = template.Library()


@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()


@register.filter(name='has_groups')
def has_groups(user, groups_names):
    groups = Group.objects.filter(name__in=[g for g in groups_names.split(',')])
    return set(groups).intersection(set(user.groups.all()))

@register.filter(name='index')
def index(List, i):
    return List[int(i)]

@register.filter(name='get_type')
def get_type(value):
    return type(value)

