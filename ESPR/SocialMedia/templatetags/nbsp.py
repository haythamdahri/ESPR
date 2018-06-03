import re

from django import template
from django.utils.safestring import mark_safe
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


register = template.Library()

@register.filter()
def nbsp_Link(value):
    lines = value.split('\n')
    values = ""
    for line in lines:
        words = line.split(' ')
        for val in words:
            regex = re.compile(
                r'^((?:http|ftp)s?://)?'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)', re.IGNORECASE)
            if re.match(regex, val):
                if( "http" not in val ):
                    values += "<a target='_blank' href='http://"+val+"'>"+val+"</a>&nbsp"
                else:
                    values += "<a target='_blank' href='"+val+"'>"+val+"</a>&nbsp"
            else:
                values += val+"&nbsp"
        values = values[:-5]
    return mark_safe(values)