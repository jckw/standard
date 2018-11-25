import graphene
from graphene import relay
from graphql import GraphQLError
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.node.node import from_global_id
import graphql_jwt
from .models import (
    Customer as CustomerModel,
    Order as OrderModel,
    OrderItem as OrderItemModel,
    Item as ItemModel,
    Queue as QueueModel,
    Manager as ManagerModel
)
from django.contrib.auth.models import User
import uuid
import datetime


class Customer(DjangoObjectType):
    class Meta:
        model = CustomerModel
        interfaces = (relay.Node, )


class Order(DjangoObjectType):
    class Meta:
        model = OrderModel
        interfaces = (relay.Node, )

    position = graphene.Int()

    def resolve_position(self, info):
        return OrderModel.objects.filter(completed=False, created__lt=self.created, queue__id=self.queue.id).count()


class OrderItem(DjangoObjectType):
    class Meta:
        model = OrderItemModel
        interfaces = (relay.Node, )


class Item(DjangoObjectType):
    class Meta:
        model = ItemModel
        interfaces = (relay.Node, )


class Queue(DjangoObjectType):
    class Meta:
        model = QueueModel
        interfaces = (relay.Node, )

    length = graphene.Int()

    def resolve_length(self, info):
        return OrderModel.objects.filter(completed=False, queue__id=self.id).count()


class Manager(DjangoObjectType):
    class Meta:
        model = ManagerModel
        interfaces = (relay.Node, )


class OrderConnection(relay.Connection):
    class Meta:
        node = Order


class OrderItemConnection(relay.Connection):
    class Meta:
        node = OrderItem


class CreateCustomer(graphene.Mutation):
    ok = graphene.Boolean()
    customer = graphene.Field(lambda: Customer)
    username = graphene.String()

    def mutate(self, info):
        user = create_random_user()
        customer = CustomerModel(user=user, created=datetime.datetime.now())
        customer.save()

        ok = True
        return CreateCustomer(customer=customer, ok=ok, username=user.username)


class CreateManager(graphene.Mutation):
    ok = graphene.Boolean()
    manager = graphene.Field(lambda: Manager)

    def mutate(self, info):
        user = create_random_user()
        manager = ManagerModel(user=user)
        manager.save()

        ok = True
        return CreateManager(manager=manager, ok=ok)


class CreateQueue(graphene.Mutation):
    ok = graphene.Boolean()
    queue = graphene.Field(lambda: Queue)

    class Arguments:
        name = graphene.String()

    def mutate(self, info, name):
        queue = QueueModel(name=name)
        queue.save()

        ok = True
        return CreateQueue(queue=queue, ok=ok)


class PlaceOrder(graphene.Mutation):
    ok = graphene.Boolean()
    customer = graphene.Field(lambda: Customer)
    queue = graphene.Field(lambda: Queue)
    order = graphene.Field(lambda: Order)

    class Arguments:
        customer_id = graphene.ID()
        queue_id = graphene.ID()

    def mutate(self, info, customer_id, queue_id):
        _, customer = from_global_id(customer_id)
        _, queue = from_global_id(queue_id)

        customer = CustomerModel.objects.get(id=customer)
        queue = QueueModel.objects.get(id=queue)

        order = OrderModel(customer=customer, queue=queue,
                           created=datetime.datetime.now())
        order.save()

        ok = True
        return PlaceOrder(customer=customer, queue=queue, order=order, ok=ok)


class PlaceOrderItem(graphene.Mutation):
    ok = graphene.Boolean()
    item = graphene.Field(lambda: Item)
    order = graphene.Field(lambda: Queue)
    order_item = graphene.Field(lambda: OrderItem)

    class Arguments:
        item_id = graphene.ID()
        order_id = graphene.ID()

    # TODO: Auth
    def mutate(self, info, item_id, order_id):
        _, item = from_global_id(item_id)
        _, order = from_global_id(order_id)

        item = ItemModel.objects.get(id=item)
        order = OrderModel.objects.get(id=order)

        order_item, _ = OrderItemModel.objects.get_or_create(
            order=order, item=item, defaults={'quantity': 0})
        order_item.quantity += 1
        order_item.save()

        ok = True
        return PlaceOrderItem(item=item, order=order, order_item=order_item, ok=ok)


class CreateItem(graphene.Mutation):
    ok = graphene.Boolean()
    item = graphene.Field(lambda: Item)
    queue = graphene.Field(lambda: Queue)

    class Arguments:
        queue_id = graphene.ID()
        name = graphene.String()

   # TODO: Auth
    def mutate(self, info, queue_id, name):
        _, queue = from_global_id(queue_id)

        queue = QueueModel.objects.get(id=queue)
        item = ItemModel(name=name, queue=queue)
        item.save()

        return CreateItem(item=item, queue=queue, ok=True)


def create_random_user():
    userpass = str(uuid.uuid4())
    return User.objects.create_user(username=userpass, password=userpass)


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    queue = relay.Node.Field(Queue)
    order = relay.Node.Field(Order)


class Mutation(graphene.ObjectType):
    place_order = PlaceOrder.Field()
    place_order_item = PlaceOrderItem.Field()
    create_customer = CreateCustomer.Field()
    create_manager = CreateManager.Field()
    create_queue = CreateQueue.Field()
    create_item = CreateItem.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
