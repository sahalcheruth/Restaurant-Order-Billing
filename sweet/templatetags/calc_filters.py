from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def calc_total(orderitems):
    total = 0
    for item in orderitems:
        total += item.menu_item.price * item.quantity
    return total




@register.filter
def multiply(value, arg):
    return value * arg
