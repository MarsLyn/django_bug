from django import template


register = template.Library()


@register.simple_tag()
def byte_convert(num):
    K = 1024
    M = 1024**2
    G = 1024**3

    if num > G:
        return '%.2f GB' % (num / G)
    elif num > M:
        return '%.2f MB' % (num / M)
    elif num > K:
        return '%.2f KB' % (num / K)
    else:
        return '%d B' % num