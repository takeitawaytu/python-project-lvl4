from django import template
from django.urls import reverse_lazy

register = template.Library()


@register.simple_tag(name='filter_url_by_user')
def get_absolute_filter_url_by_user() -> str:
    """
    Get absolute url use query string.
    Returns:
        str:
    """
    query_str = '{url}?self_tasks=on'
    return query_str.format(url=reverse_lazy('tasks'))


@register.simple_tag(name='filter_url_to_user')
def get_absolute_filter_url_to_user(user_id: int) -> str:
    """
    Get absolute url use query string.
    Args:
        user_id:
    Returns:
        str:
    """
    query_str = '{url}?executor={executor}'
    return query_str.format(url=reverse_lazy('tasks'), executor=user_id)
