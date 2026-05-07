from decimal import Decimal, ROUND_FLOOR

from django.core.exceptions import ValidationError
from django.db import models


ZERO = Decimal("0")


class Tool(models.Model):
    name = models.CharField(max_length=120, unique=True)
    usage_count = models.PositiveIntegerField("utilisations")
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    @property
    def cost_per_use(self) -> Decimal:
        if not self.usage_count:
            return ZERO
        return self.price / Decimal(self.usage_count)


class Consumable(models.Model):
    class Dimension(models.TextChoices):
        ML = "ml", "ml"
        G = "g", "g"
        PIECE = "piece", "piece"

    name = models.CharField(max_length=120, unique=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    dimension = models.CharField(max_length=10, choices=Dimension.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    @property
    def unit_cost(self) -> Decimal:
        if self.quantity <= ZERO:
            return ZERO
        return self.price / self.quantity


class Stock(models.Model):
    tool = models.OneToOneField(Tool, null=True, blank=True, on_delete=models.CASCADE)
    consumable = models.OneToOneField(Consumable, null=True, blank=True, on_delete=models.CASCADE)
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=ZERO)

    class Meta:
        ordering = ("tool__name", "consumable__name")

    def __str__(self) -> str:
        return f"{self.item_name} ({self.current_quantity})"

    def clean(self) -> None:
        has_tool = self.tool_id is not None
        has_consumable = self.consumable_id is not None
        if has_tool == has_consumable:
            raise ValidationError("Le stock doit être lié à un tool ou à un consommable, pas les deux.")

    @property
    def item_name(self) -> str:
        if self.tool:
            return self.tool.name
        if self.consumable:
            return self.consumable.name
        return "Item inconnu"

    @property
    def item_kind(self) -> str:
        return "Tool" if self.tool_id else "Consommable"

    @property
    def item_unit(self) -> str:
        if self.consumable_id:
            return self.consumable.dimension
        return "piece"

    def add_quantity(self, quantity: Decimal) -> None:
        updated = self.current_quantity + quantity
        if updated < ZERO:
            raise ValidationError("Le stock ne peut pas devenir négatif.")
        self.current_quantity = updated
        self.save(update_fields=["current_quantity"])


class Set(models.Model):
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def fabrication_cost(self) -> Decimal:
        total = ZERO
        for item in self.items.select_related("tool", "consumable"):
            total += item.cost_for_requirement()
        return total.quantize(Decimal("0.01"))

    def max_producible(self) -> int:
        consumable_items = [item for item in self.items.select_related("consumable") if item.consumable_id]
        if not consumable_items:
            return 0

        capacities = []
        for item in consumable_items:
            stock = Stock.objects.filter(consumable=item.consumable).first()
            if not stock or item.required_quantity <= ZERO:
                capacities.append(0)
                continue
            capacity = (stock.current_quantity / item.required_quantity).to_integral_value(rounding=ROUND_FLOOR)
            capacities.append(int(capacity))
        return min(capacities) if capacities else 0

    def low_stock_items(self, threshold: int = 2) -> list["SetItem"]:
        flagged = []
        for item in self.items.select_related("consumable"):
            if not item.consumable_id or item.required_quantity <= ZERO:
                continue
            stock = Stock.objects.filter(consumable=item.consumable).first()
            current = stock.current_quantity if stock else ZERO
            capacity = int((current / item.required_quantity).to_integral_value(rounding=ROUND_FLOOR)) if current > ZERO else 0
            if capacity <= threshold:
                flagged.append(item)
        return flagged


class SetItem(models.Model):
    set = models.ForeignKey(Set, related_name="items", on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, null=True, blank=True, on_delete=models.CASCADE)
    consumable = models.ForeignKey(Consumable, null=True, blank=True, on_delete=models.CASCADE)
    required_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("1.00"))

    class Meta:
        ordering = ("id",)

    def __str__(self) -> str:
        if self.tool_id:
            return self.item_name
        return f"{self.item_name} x {self.required_quantity}"

    def clean(self) -> None:
        has_tool = self.tool_id is not None
        has_consumable = self.consumable_id is not None
        if has_tool == has_consumable:
            raise ValidationError("Chaque ligne du set doit référencer un tool ou un consommable.")
        if has_tool:
            self.required_quantity = Decimal("1.00")
        elif self.required_quantity <= ZERO:
            raise ValidationError("Un consommable doit avoir une quantité requise supérieure à zéro.")

    @property
    def item_name(self) -> str:
        return self.tool.name if self.tool_id else self.consumable.name

    @property
    def item_kind(self) -> str:
        return "Tool" if self.tool_id else "Consommable"

    def cost_for_requirement(self) -> Decimal:
        if self.tool_id:
            return self.tool.cost_per_use
        return self.consumable.unit_cost * self.required_quantity
