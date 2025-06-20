from django.shortcuts import render, redirect, get_object_or_404
from .models import SweetTable, MenuItem, Meal, FriedItem, Juice, Order, OrderItem, OrderMeal, OrderFried, OrderJuice
from django.db.models import F, Sum, ExpressionWrapper, DecimalField
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import csv

def home(request):
    if request.method == 'POST':
        table_id = request.POST.get('table')
        if table_id:
            return redirect('order_items', table_id=table_id)
    numbers = list(range(1, 21))
    return render(request, 'home.html', {'numbers': numbers})

def order_items(request, table_id):
    table = SweetTable.objects.get(id=table_id)
    menu_items = MenuItem.objects.all()
    meals = Meal.objects.all()
    fried_items = FriedItem.objects.all()
    juices = Juice.objects.all()

    if request.method == 'POST':
        order = Order.objects.create(table=table)

        for item in menu_items:
            qty = request.POST.get(f'quantity_menu_{item.id}')
            if qty and int(qty) > 0:
                OrderItem.objects.create(order=order, menu_item=item, quantity=int(qty))

        for meal in meals:
            qty = request.POST.get(f'quantity_meal_{meal.id}')
            if qty and int(qty) > 0:
                OrderMeal.objects.create(order=order, meal=meal, quantity=int(qty))

        for fried in fried_items:
            qty = request.POST.get(f'quantity_fried_{fried.id}')
            if qty and int(qty) > 0:
                OrderFried.objects.create(order=order, fried_item=fried, quantity=int(qty))

        for juice in juices:
            qty = request.POST.get(f'quantity_juice_{juice.id}')
            if qty and int(qty) > 0:
                OrderJuice.objects.create(order=order, juice=juice, quantity=int(qty))

        return redirect('order_detail', order_id=order.id)

    return render(request, 'order_items.html', {
        'table': table,
        'menu_items': menu_items,
        'meals': meals,
        'fried_items': fried_items,
        'juices': juices,
    })

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    meals = order.meal_items.all()
    fried_items = order.fried_items.all()
    juices = order.juices.all()

    menu_items = MenuItem.objects.exclude(id__in=items.values_list('menu_item_id', flat=True))
    meal_items = Meal.objects.exclude(id__in=meals.values_list('meal_id', flat=True))
    fried_list = FriedItem.objects.exclude(id__in=fried_items.values_list('fried_item_id', flat=True))
    juice_list = Juice.objects.exclude(id__in=juices.values_list('juice_id', flat=True))

    if request.method == 'POST':
        if 'delete' in request.POST:
            OrderItem.objects.filter(id=request.POST.get('delete'), order=order).delete()
        elif 'delete_meal' in request.POST:
            OrderMeal.objects.filter(id=request.POST.get('delete_meal'), order=order).delete()
        elif 'delete_fried' in request.POST:
            OrderFried.objects.filter(id=request.POST.get('delete_fried'), order=order).delete()
        elif 'delete_juice' in request.POST:
            OrderJuice.objects.filter(id=request.POST.get('delete_juice'), order=order).delete()

        elif 'update' in request.POST:
            for item in items:
                qty = request.POST.get(f'quantity_{item.id}')
                if qty: item.quantity = int(qty); item.save()
            for meal in meals:
                qty = request.POST.get(f'meal_quantity_{meal.id}')
                if qty: meal.quantity = int(qty); meal.save()
            for fried in fried_items:
                qty = request.POST.get(f'fried_quantity_{fried.id}')
                if qty: fried.quantity = int(qty); fried.save()
            for juice in juices:
                qty = request.POST.get(f'juice_quantity_{juice.id}')
                if qty: juice.quantity = int(qty); juice.save()

        elif 'add_item' in request.POST:
            menu_item = get_object_or_404(MenuItem, id=request.POST.get('add_item'))
            qty = int(request.POST.get(f'new_qty_{menu_item.id}'))
            OrderItem.objects.update_or_create(order=order, menu_item=menu_item, defaults={'quantity': qty})

        elif 'add_meal' in request.POST:
            meal = get_object_or_404(Meal, id=request.POST.get('add_meal'))
            qty = int(request.POST.get(f'new_meal_qty_{meal.id}'))
            OrderMeal.objects.update_or_create(order=order, meal=meal, defaults={'quantity': qty})

        elif 'add_fried' in request.POST:
            fried = get_object_or_404(FriedItem, id=request.POST.get('add_fried'))
            qty = int(request.POST.get(f'new_fried_qty_{fried.id}'))
            OrderFried.objects.update_or_create(order=order, fried_item=fried, defaults={'quantity': qty})

        elif 'add_juice' in request.POST:
            juice = get_object_or_404(Juice, id=request.POST.get('add_juice'))
            qty = int(request.POST.get(f'new_juice_qty_{juice.id}'))
            OrderJuice.objects.update_or_create(order=order, juice=juice, defaults={'quantity': qty})

        elif 'save' in request.POST:
            return redirect('saved_orders')

        return redirect('order_detail', order_id=order.id)

    total_price = (
        sum(i.menu_item.price * i.quantity for i in items) +
        sum(m.meal.price * m.quantity for m in meals) +
        sum(f.fried_item.price * f.quantity for f in fried_items) +
        sum(j.juice.price * j.quantity for j in juices)
    )

    return render(request, 'order_detail.html', {
        'order': order,
        'items': items,
        'meals': meals,
        'fried_items': fried_items,
        'juices': juices,
        'menu_items': menu_items,
        'meal_items': meal_items,
        'fried_list': fried_list,
        'juice_list': juice_list,
        'total_price': total_price,
    })

from django.shortcuts import render
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from .models import Order, OrderItem, OrderMeal, OrderFried, OrderJuice

def saved_orders(request):
    orders = Order.objects.all().order_by('-created_at')

    # Filters from GET parameters
    table_num = request.GET.get('table')
    if table_num:
        orders = orders.filter(table__number=table_num)

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    status = request.GET.get('status')
    if status == 'finalized':
        orders = orders.filter(finalized=True)
    elif status == 'not_finalized':
        orders = orders.filter(finalized=False)

    # Total sales calculations
    sales_expr = ExpressionWrapper(F('menu_item__price') * F('quantity'), output_field=DecimalField())
    meal_expr = ExpressionWrapper(F('meal__price') * F('quantity'), output_field=DecimalField())
    fried_expr = ExpressionWrapper(F('fried_item__price') * F('quantity'), output_field=DecimalField())
    juice_expr = ExpressionWrapper(F('juice__price') * F('quantity'), output_field=DecimalField())

    item_total = OrderItem.objects.filter(order__in=orders).aggregate(total=Sum(sales_expr))['total'] or 0
    meal_total = OrderMeal.objects.filter(order__in=orders).aggregate(total=Sum(meal_expr))['total'] or 0
    fried_total = OrderFried.objects.filter(order__in=orders).aggregate(total=Sum(fried_expr))['total'] or 0
    juice_total = OrderJuice.objects.filter(order__in=orders).aggregate(total=Sum(juice_expr))['total'] or 0

    total_sales = item_total + meal_total + fried_total + juice_total

    return render(request, 'savedorders.html', {
        'orders': orders,
        'filter_table': table_num or '',
        'filter_date_from': date_from or '',
        'filter_date_to': date_to or '',
        'filter_status': status or '',
        'total_sales': total_sales,
    })

import csv
from django.http import HttpResponse
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from datetime import datetime
from .models import Order

def download_orders_csv(request):
    orders = Order.objects.all().order_by('-created_at')

    # Apply same filters as saved_orders view
    table_num = request.GET.get('table')
    if table_num:
        orders = orders.filter(table__number=table_num)

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    status = request.GET.get('status')
    if status == 'finalized':
        orders = orders.filter(finalized=True)
    elif status == 'not_finalized':
        orders = orders.filter(finalized=False)

    today = datetime.now().strftime('%Y-%m-%d')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="filtered_orders_{today}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Table Number', 'Created At', 'Items', 'Total Price'])

    grand_total = 0

    for order in orders:
        parts = (
            [f"{i.menu_item.name} x {i.quantity}" for i in order.items.all()] +
            [f"{m.meal.name} x {m.quantity}" for m in order.meal_items.all()] +
            [f"{f.fried_item.name} x {f.quantity}" for f in order.fried_items.all()] +
            [f"{j.juice.name} x {j.quantity}" for j in order.juices.all()]
        )
        total = (
            sum(i.menu_item.price * i.quantity for i in order.items.all()) +
            sum(m.meal.price * m.quantity for m in order.meal_items.all()) +
            sum(f.fried_item.price * f.quantity for f in order.fried_items.all()) +
            sum(j.juice.price * j.quantity for j in order.juices.all())
        )
        grand_total += total
        writer.writerow([
            order.id,
            order.table.number,
            order.created_at.strftime("%Y-%m-%d %H:%M"),
            "; ".join(parts),
            f"{total:.2f}"
        ])

    writer.writerow([])
    writer.writerow(['', '', '', 'Grand Total', f"{grand_total:.2f}"])

    return response

@require_POST
def delete_orders(request):
    ids = request.POST.getlist('order_ids')
    if ids:
        Order.objects.filter(id__in=ids).delete()
        messages.success(request, f"{len(ids)} order(s) deleted successfully.")
    else:
        messages.warning(request, "No orders selected for deletion.")
    return redirect('saved_orders')




