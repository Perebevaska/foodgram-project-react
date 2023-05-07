from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from recipes.models import Ingredient


class IngredientResource(resources.ModelResource):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


@admin.register(Ingredient)
class AdminIngredient(ImportExportModelAdmin):
    resource_classes = [IngredientResource]
    list_display = (
        'name',
        'measurement_unit',
    )
    list_filter = ('name',)
