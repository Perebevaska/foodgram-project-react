from django.contrib import admin
from users.models import Subscription, User


@admin.register(User)
class AdminCustomUser(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'password',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = (
        'username',
        'email',
    )


@admin.register(Subscription)
class AdminSubscriptions(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
