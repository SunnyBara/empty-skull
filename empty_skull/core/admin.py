from django.contrib import admin

from .models import Consumable, FavoriteItem, Set, SetItem, Stock, Tool


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ("name", "usage_count", "price", "cost_per_use")
    search_fields = ("name",)


@admin.register(Consumable)
class ConsumableAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "dimension", "price", "unit_cost")
    search_fields = ("name",)


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("item_name", "item_kind", "current_quantity")
    list_filter = ("tool", "consumable")


@admin.register(FavoriteItem)
class FavoriteItemAdmin(admin.ModelAdmin):
    list_display = ("item_name", "item_kind", "required_quantity")
    list_filter = ("tool", "consumable")


class SetItemInline(admin.TabularInline):
    model = SetItem
    extra = 1


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ("name", "image", "fabrication_cost", "max_producible")
    search_fields = ("name",)
    inlines = [SetItemInline]
