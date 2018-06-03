from django import template

register = template.Library()


@register.filter
def coma_dot(value):
    return str(value).replace(",", ".")
