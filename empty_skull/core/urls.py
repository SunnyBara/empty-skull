from django.urls import path

from .views import (
    ConsumableDeleteView,
    ConsumableUpdateView,
    DataView,
    FavoritesView,
    HomeView,
    ProductionView,
    SetCreateView,
    SetDeleteView,
    SetDetailView,
    SetListView,
    SetUpdateView,
    StockView,
    ToolDeleteView,
    ToolUpdateView,
)


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("data/", DataView.as_view(), name="data"),
    path("favorites/", FavoritesView.as_view(), name="favorites"),
    path("stock/", StockView.as_view(), name="stock"),
    path("sets/", SetListView.as_view(), name="set-list"),
    path("sets/create/", SetCreateView.as_view(), name="set-create"),
    path("sets/<int:pk>/", SetDetailView.as_view(), name="set-detail"),
    path("sets/<int:pk>/edit/", SetUpdateView.as_view(), name="set-update"),
    path("sets/<int:pk>/delete/", SetDeleteView.as_view(), name="set-delete"),
    path("production/", ProductionView.as_view(), name="production"),
    path("tools/<int:pk>/edit/", ToolUpdateView.as_view(), name="tool-update"),
    path("tools/<int:pk>/delete/", ToolDeleteView.as_view(), name="tool-delete"),
    path("consumables/<int:pk>/edit/", ConsumableUpdateView.as_view(), name="consumable-update"),
    path("consumables/<int:pk>/delete/", ConsumableDeleteView.as_view(), name="consumable-delete"),
]
