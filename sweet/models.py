from django.db import models

class Table(models.Model):
    number = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"Table {self.number}"

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name




class Meal(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


class OrderMeal(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='meal_items')  # use string here
    meal = models.ForeignKey('Meal', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.meal.name} x {self.quantity}"



class SweetTable(models.Model):
    number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Table {self.number}"
    
    
class Order(models.Model):
    table = models.ForeignKey(SweetTable, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    finalized = models.BooleanField(default=False)  # new field

    def __str__(self):
        return f"Order #{self.id} - {self.table}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"






class FriedItem(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

class Juice(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)

class OrderFried(models.Model):
    order = models.ForeignKey(Order, related_name='fried_items', on_delete=models.CASCADE)
    fried_item = models.ForeignKey(FriedItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

class OrderJuice(models.Model):
    order = models.ForeignKey(Order, related_name='juices', on_delete=models.CASCADE)
    juice = models.ForeignKey(Juice, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
