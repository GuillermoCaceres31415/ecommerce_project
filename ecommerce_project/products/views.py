# products/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Product, Cart, CartItem, Order, OrderItem
from .serializers import ProductSerializer, CartSerializer, OrderSerializer


# Usa Generic Views (RICHIESTO) con permission standard
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # ← Permission standard

    def perform_create(self, serializer):
        # Solo utenti staff possono creare prodotti per ora
        if not self.request.user.is_staff:
            return Response(
                {'error': 'Only staff can create products'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # ← Permission standard

    def perform_update(self, serializer):
        # Solo utenti staff possono modificare prodotti
        if not self.request.user.is_staff:
            return Response(
                {'error': 'Only staff can update products'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()

    def perform_destroy(self, instance):
        # Solo utenti staff possono eliminare prodotti
        if not self.request.user.is_staff:
            return Response(
                {'error': 'Only staff can delete products'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance.delete()


# Business Logic per Cart
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        if not product.is_available():
            return Response(
                {'error': 'Product not available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return Response({
            'message': 'Product added to cart',
            'cart_item_id': cart_item.id,
            'quantity': cart_item.quantity
        })
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    except Cart.DoesNotExist:
        return Response({'items': [], 'message': 'Cart is empty'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, product_id):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.delete()
        return Response({'message': 'Product removed from cart'})
    except (Cart.DoesNotExist, CartItem.DoesNotExist):
        return Response(
            {'error': 'Item not found in cart'},
            status=status.HTTP_404_NOT_FOUND
        )


# Order Processing con Business Logic
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return Response(
                {'error': 'Cart is empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calcola totale e verifica disponibilità
        total_amount = 0
        for item in cart.items.all():
            if not item.product.is_available() or item.product.stock_quantity < item.quantity:
                return Response(
                    {'error': f'Product {item.product.name} not available in requested quantity'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            total_amount += item.product.price * item.quantity

        # Verifica che ci sia un indirizzo di spedizione
        shipping_address = request.data.get('shipping_address', '')
        if not shipping_address:
            return Response(
                {'error': 'Shipping address is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crea ordine
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            shipping_address=shipping_address
        )

        # Crea order items e aggiorna stock
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Aggiorna stock
            item.product.stock_quantity -= item.quantity
            item.product.save()

        # Svuota carrello
        cart.items.all().delete()

        return Response({
            'message': 'Order created successfully',
            'order_id': order.id,
            'total': str(total_amount),
            'status': order.status
        })

    except Cart.DoesNotExist:
        return Response(
            {'error': 'Cart not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# Vista per moderatori/staff - gestione ordini
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_orders(request):
    # Solo staff può vedere tutti gli ordini
    if not request.user.is_staff:
        return Response(
            {'error': 'Only staff can view all orders'},
            status=status.HTTP_403_FORBIDDEN
        )

    orders = Order.objects.all().order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    # Solo staff può aggiornare lo status degli ordini
    if not request.user.is_staff:
        return Response(
            {'error': 'Only staff can update order status'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        order = Order.objects.get(id=order_id)
        new_status = request.data.get('status')

        if new_status not in dict(Order.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        return Response({
            'message': 'Order status updated',
            'order_id': order.id,
            'new_status': order.status
        })

    except Order.DoesNotExist:
        return Response(
            {'error': 'Order not found'},
            status=status.HTTP_404_NOT_FOUND
        )