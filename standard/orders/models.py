from django.conf import settings
from django.db import models


class Customer(models.Model):
    created = models.DateTimeField(auto_created=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)


class Queue(models.Model):
    name = models.CharField(max_length=50)


class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    queue = models.ForeignKey('Queue', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_created=True, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = (('customer', 'queue'),)


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


class Item(models.Model):
    name = models.CharField(max_length=100)
    queue = models.ForeignKey('Queue', on_delete=models.CASCADE, null=True)


class Manager(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
