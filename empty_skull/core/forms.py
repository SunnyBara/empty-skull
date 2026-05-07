from decimal import Decimal

from django import forms
from django.forms import inlineformset_factory

from .models import Consumable, Set, SetItem, Stock, Tool


class ToolForm(forms.ModelForm):
    class Meta:
        model = Tool
        fields = ("name", "usage_count", "price")


class ConsumableForm(forms.ModelForm):
    class Meta:
        model = Consumable
        fields = ("name", "quantity", "dimension", "price")


class SetForm(forms.ModelForm):
    class Meta:
        model = Set
        fields = ("name",)


class SetItemForm(forms.ModelForm):
    ITEM_CHOICES = (
        ("tool", "Tool"),
        ("consumable", "Consommable"),
    )

    item_type = forms.ChoiceField(
        choices=ITEM_CHOICES,
        widget=forms.RadioSelect,
        initial="consumable",
    )
    required_quantity = forms.DecimalField(min_value=Decimal("0.01"), decimal_places=2, max_digits=10, required=False)

    class Meta:
        model = SetItem
        fields = ("item_type", "tool", "consumable", "required_quantity")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["item_type"].initial = "tool" if self.instance.tool_id else "consumable"

    def clean(self):
        cleaned = super().clean()
        item_type = cleaned.get("item_type")
        tool = cleaned.get("tool")
        consumable = cleaned.get("consumable")

        if item_type == "tool":
            cleaned["consumable"] = None
            cleaned["required_quantity"] = Decimal("1.00")
            if not tool:
                raise forms.ValidationError("Sélectionnez un tool.")
        elif item_type == "consumable":
            cleaned["tool"] = None
            if not cleaned.get("required_quantity"):
                raise forms.ValidationError("Saisissez une quantité requise pour le consommable.")
            if not consumable:
                raise forms.ValidationError("Sélectionnez un consommable.")
        else:
            raise forms.ValidationError("Choisir soit un tool soit un consommable.")
        return cleaned


SetItemFormSet = inlineformset_factory(
    Set,
    SetItem,
    form=SetItemForm,
    extra=0,
    can_delete=True,
)


class StockAdjustmentForm(forms.Form):
    ITEM_CHOICES = (
        ("tool", "Tool"),
        ("consumable", "Consommable"),
    )

    item_type = forms.ChoiceField(
        choices=ITEM_CHOICES,
        widget=forms.RadioSelect,
        initial="consumable",
    )
    tool = forms.ModelChoiceField(queryset=Tool.objects.all(), required=False)
    consumable = forms.ModelChoiceField(queryset=Consumable.objects.all(), required=False)
    quantity = forms.DecimalField(
        min_value=Decimal("0.01"),
        decimal_places=2,
        max_digits=10,
        label="Nombre d'unités à ajouter",
    )

    def clean(self):
        cleaned = super().clean()
        item_type = cleaned.get("item_type")
        tool = cleaned.get("tool")
        consumable = cleaned.get("consumable")

        if item_type == "tool" and not tool:
            raise forms.ValidationError("Sélectionnez un tool.")
        if item_type == "consumable" and not consumable:
            raise forms.ValidationError("Sélectionnez un consommable.")
        return cleaned

    def save(self) -> Stock:
        item_type = self.cleaned_data["item_type"]
        quantity = self.cleaned_data["quantity"]
        if item_type == "tool":
            stock, _ = Stock.objects.get_or_create(tool=self.cleaned_data["tool"])
            added_quantity = quantity
        else:
            consumable = self.cleaned_data["consumable"]
            stock, _ = Stock.objects.get_or_create(consumable=consumable)
            added_quantity = quantity * consumable.quantity
        stock.add_quantity(added_quantity)
        return stock


class StockManualUpdateForm(forms.Form):
    stock_id = forms.IntegerField(widget=forms.HiddenInput)
    current_quantity = forms.DecimalField(
        min_value=Decimal("0.00"),
        decimal_places=2,
        max_digits=10,
        label="Stock courant",
    )

    def clean_stock_id(self):
        stock_id = self.cleaned_data["stock_id"]
        if not Stock.objects.filter(pk=stock_id).exists():
            raise forms.ValidationError("Stock introuvable.")
        return stock_id

    def save(self) -> Stock:
        stock = Stock.objects.get(pk=self.cleaned_data["stock_id"])
        stock.current_quantity = self.cleaned_data["current_quantity"]
        stock.save(update_fields=["current_quantity"])
        return stock


class ProductionForm(forms.Form):
    set = forms.ModelChoiceField(queryset=Set.objects.all())
    quantity = forms.IntegerField(min_value=1, initial=1)

    def clean(self):
        cleaned = super().clean()
        selected_set = cleaned.get("set")
        quantity = cleaned.get("quantity")
        if selected_set and quantity and selected_set.max_producible() < quantity:
            raise forms.ValidationError("Le stock actuel ne permet pas cette production.")
        return cleaned
