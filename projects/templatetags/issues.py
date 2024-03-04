from django import template


register = template.Library()


@register.simple_tag()
def num_just(num):
    if num < 100:
        new_num = str(num).rjust(3, '0')
    return f"#{new_num}"

