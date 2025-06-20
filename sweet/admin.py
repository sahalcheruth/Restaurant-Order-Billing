from django.contrib import admin

from .models import FriedItem, Juice, OrderFried, OrderJuice
# Register your models here.
from django.contrib import admin
from .models import Meal,MenuItem  # Import your model

admin.site.register(Meal)

admin.site.register(MenuItem)  # Register the Meal model


admin.site.register(FriedItem)
admin.site.register(Juice)
admin.site.register(OrderFried)
admin.site.register(OrderJuice)
