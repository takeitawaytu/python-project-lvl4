from django import template
from django.urls import reverse_lazy

register = template.Library()


@register.simple_tag(name='filter_url')
def get_absolute_filter_url(label_id: int) -> str:
    """
    Get absolute url use query string.
    Args:
        label_id:
    Returns:
        str:
    """
    query_str = '{url}?label={label}'
    return query_str.format(url=reverse_lazy('tasks'), label=label_id)
