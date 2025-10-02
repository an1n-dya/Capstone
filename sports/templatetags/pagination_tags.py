from django import template

register = template.Library()

@register.simple_tag
def url_replace(request, **kwargs):
    """
    Replace or add GET parameters in the current URL.
    Usage: {% url_replace request page=3 %}
    """
    query = request.GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()
