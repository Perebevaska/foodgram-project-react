from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from users.models import User


class UserResource(resources.ModelResource):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    resource_classes = [UserResource]
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    search_fields = ('username',)
    list_filter = ('username',)
    empty_value_display = '-пусто-'


