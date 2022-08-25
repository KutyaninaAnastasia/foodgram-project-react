from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import viewsets, views, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import RecipeFilter, IngredientFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from .serializers import (TagSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          FavoriteRecipeSerializer, ShoppingCartSerializer)
from recipes.models import (Tag, Ingredient, FavoriteRecipe, Recipe,
                            AmountIngredient, ShoppingCart)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = [IngredientFilter]
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    serializer_class = RecipeSerializer
    pagination_class = CustomPageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @staticmethod
    def post_method_for_actions(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method_for_actions(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated], )
    def favorite(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=FavoriteRecipeSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=FavoriteRecipe)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated], )
    def shopping_cart(self, request, pk):
        return self.post_method_for_actions(
            request=request, pk=pk, serializers=ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method_for_actions(
            request=request, pk=pk, model=ShoppingCart)


class DownloadShoppingCart(views.APIView):
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get(self, request):
        final_cart = {}
        ingredients = AmountIngredient.objects.filter(
            recipe__shoppingcart__user=request.user).values(
            'ingredient__name', 'ingredient__measurement_unit').annotate(
            total=Sum('amount')).order_by('ingredient__name')
        for item in ingredients:
            name = item['ingredient__name']
            final_cart[name] = {
                'measurement_unit': item['ingredient__measurement_unit'],
                'total': item['total']
            }
        pdfmetrics.registerFont(
            TTFont('RobotoItalic', 'data/RobotoItalic.ttf', 'UTF-8'))
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.pdf"')
        page = canvas.Canvas(response)
        page.setFont('RobotoItalic', size=30)
        page.drawString(200, 800, 'Список покупок')
        page.setFont('RobotoItalic', size=18)
        height = 750
        for i, (name, data) in enumerate(final_cart.items(), 1):
            page.drawString(75, height, (f'{i}. {name} - {data["total"]} '
                                         f'{data["measurement_unit"]}'))
            height -= 25
        page.showPage()
        page.save()
        return response
