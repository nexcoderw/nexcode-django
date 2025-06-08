from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, *url_names):
    """
    Usage  →  class="top-menu__link {% active 'dashboard' 'projects' … %}"
    Returns →  'top-menu__link--active' if the current view´s url_name
               matches any of the names supplied.
    """
    request = context.get("request")
    if not request or not request.resolver_match:
        return ""
    return "top-menu__link--active" if request.resolver_match.url_name in url_names else ""
