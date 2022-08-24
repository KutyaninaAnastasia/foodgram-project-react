from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


class Tag(models.Model):
    GREEN = '#71bc78'
    BLUE = '#00bfff'
    YELLOW = '#fff44f'
    ORANGE = '#ffcc00'
    PINK = '#fb7efd'

    COLOR_CHOICES = [
        (GREEN, 'Зеленый'),
        (BLUE, 'Синий'),
        (YELLOW, 'Желтый'),
        (ORANGE, 'Оранжевый'),
        (PINK, 'Розовый'),
    ]
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название',
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='HEX-код',
        null=True,
        blank=True,
        choices=COLOR_CHOICES
    )
    slug = models.CharField(
        max_length=200,
        unique=True,
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения ингредиента',
        max_length=200,
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique ingredient')
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    image = models.ImageField(
        upload_to='static/recipes/',
        verbose_name='Изображение блюда',
        blank=True,
        null=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='AmountIngredient',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.IntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Минимальное время приготовления: 1 минута'
            )
        ],
        verbose_name='Время приготовления',
    )

    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.author.email}, {self.name}'


class AmountIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
    )
    amount = models.IntegerField(
        verbose_name='Количество ингредиентов',
        default=1,
        validators=[
            MinValueValidator(
                1,
                message='Минимальное количество продукта: 1'
            )
        ],
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']
        constraints = (
            models.UniqueConstraint(
                fields=('ingredient', 'recipe',),
                name='unique ingredient amount',
            ),
        )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='favorites',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique favorite')
        ]


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='shoppingcart',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
        related_name='shoppingcart',
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique shoppingcart')
        ]
