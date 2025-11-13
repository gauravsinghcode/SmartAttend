from django import template
register = template.Library()

@register.filter
def pluck(data_list, key):
    return [item.get(key) for item in data_list]
