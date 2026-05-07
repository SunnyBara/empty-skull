from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.views import View
from django.views.generic import DeleteView, UpdateView

from .forms import (
    ConsumableForm,
    ProductionForm,
    SetForm,
    SetItemFormSet,
    StockAdjustmentForm,
    StockManualUpdateForm,
    ToolForm,
)
from .models import Consumable, Set, SetItem, Stock, Tool


def ensure_stock_records() -> None:
    for tool in Tool.objects.all():
        Stock.objects.get_or_create(tool=tool)
    for consumable in Consumable.objects.all():
        Stock.objects.get_or_create(consumable=consumable)


def push_low_stock_messages(request: HttpRequest) -> None:
    for set_obj in Set.objects.all():
        if set_obj.max_producible() <= 2:
            messages.warning(
                request,
                format_html(
                    'Pensez à réapprovisionner le stock pour faire "{}". <a href="{}">Voir le détail</a>',
                    set_obj.name,
                    reverse("set-detail", args=[set_obj.pk]),
                ),
            )


class HomeView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        return redirect("data")


class DataView(View):
    template_name = "core/data.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        ensure_stock_records()
        context = {
            "tool_form": ToolForm(prefix="tool"),
            "consumable_form": ConsumableForm(prefix="consumable"),
            "tools": Tool.objects.all(),
            "consumables": Consumable.objects.all(),
            "sets": Set.objects.all(),
        }
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        ensure_stock_records()
        if "create_tool" in request.POST:
            tool_form = ToolForm(request.POST, prefix="tool")
            consumable_form = ConsumableForm(prefix="consumable")
            if tool_form.is_valid():
                tool = tool_form.save()
                Stock.objects.get_or_create(tool=tool)
                messages.success(request, "Tool ajouté.")
                return redirect("data")
        elif "create_consumable" in request.POST:
            tool_form = ToolForm(prefix="tool")
            consumable_form = ConsumableForm(request.POST, prefix="consumable")
            if consumable_form.is_valid():
                consumable = consumable_form.save()
                Stock.objects.get_or_create(consumable=consumable)
                messages.success(request, "Consommable ajouté.")
                push_low_stock_messages(request)
                return redirect("data")
        else:
            return redirect("data")

        context = {
            "tool_form": tool_form,
            "consumable_form": consumable_form,
            "tools": Tool.objects.all(),
            "consumables": Consumable.objects.all(),
            "sets": Set.objects.all(),
        }
        return render(request, self.template_name, context)


class ToolUpdateView(UpdateView):
    model = Tool
    form_class = ToolForm
    template_name = "core/model_form.html"

    def get_success_url(self):
        messages.success(self.request, "Tool mis à jour.")
        return reverse("data")


class ToolDeleteView(DeleteView):
    model = Tool
    template_name = "core/confirm_delete.html"

    def get_success_url(self):
        messages.success(self.request, "Tool supprimé.")
        return reverse("data")


class ConsumableUpdateView(UpdateView):
    model = Consumable
    form_class = ConsumableForm
    template_name = "core/model_form.html"

    def get_success_url(self):
        messages.success(self.request, "Consommable mis à jour.")
        push_low_stock_messages(self.request)
        return reverse("data")


class ConsumableDeleteView(DeleteView):
    model = Consumable
    template_name = "core/confirm_delete.html"

    def get_success_url(self):
        messages.success(self.request, "Consommable supprimé.")
        return reverse("data")


class SetCreateView(View):
    template_name = "core/set_form.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        form = SetForm()
        formset = SetItemFormSet()
        return render(request, self.template_name, {"form": form, "formset": formset, "title": "Créer un set"})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SetForm(request.POST)
        formset = SetItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                set_obj = form.save()
                formset.instance = set_obj
                formset.save()
            messages.success(request, "Set créé.")
            push_low_stock_messages(request)
            return redirect("data")
        return render(request, self.template_name, {"form": form, "formset": formset, "title": "Créer un set"})


class SetUpdateView(View):
    template_name = "core/set_form.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        set_obj = get_object_or_404(Set, pk=pk)
        form = SetForm(instance=set_obj)
        formset = SetItemFormSet(instance=set_obj)
        return render(request, self.template_name, {"form": form, "formset": formset, "title": f"Modifier {set_obj.name}"})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        set_obj = get_object_or_404(Set, pk=pk)
        form = SetForm(request.POST, instance=set_obj)
        formset = SetItemFormSet(request.POST, instance=set_obj)
        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, "Set mis à jour.")
            push_low_stock_messages(request)
            return redirect("data")
        return render(request, self.template_name, {"form": form, "formset": formset, "title": f"Modifier {set_obj.name}"})


class SetDeleteView(DeleteView):
    model = Set
    template_name = "core/confirm_delete.html"

    def get_success_url(self):
        messages.success(self.request, "Set supprimé.")
        return reverse("data")


class StockView(View):
    template_name = "core/stock.html"

    @staticmethod
    def build_context(form: StockAdjustmentForm | None = None, manual_form: StockManualUpdateForm | None = None) -> dict:
        return {
            "form": form or StockAdjustmentForm(),
            "manual_form": manual_form or StockManualUpdateForm(),
            "stocks": Stock.objects.select_related("tool", "consumable"),
        }

    def get(self, request: HttpRequest) -> HttpResponse:
        ensure_stock_records()
        return render(request, self.template_name, self.build_context())

    def post(self, request: HttpRequest) -> HttpResponse:
        ensure_stock_records()
        if "reset_stocks" in request.POST:
            Stock.objects.update(current_quantity=Decimal("0.00"))
            messages.success(request, "Tous les stocks ont été remis à zéro.")
            push_low_stock_messages(request)
            return redirect("stock")

        if "reset_stock_item" in request.POST:
            stock = get_object_or_404(Stock, pk=request.POST.get("stock_id"))
            stock.current_quantity = Decimal("0.00")
            stock.save(update_fields=["current_quantity"])
            messages.success(request, f"Stock remis à zéro pour {stock.item_name}.")
            push_low_stock_messages(request)
            return redirect("stock")

        if "manual_update_stock" in request.POST:
            manual_form = StockManualUpdateForm(request.POST)
            if manual_form.is_valid():
                stock = manual_form.save()
                messages.success(request, f"Stock modifié manuellement pour {stock.item_name}.")
                push_low_stock_messages(request)
                return redirect("stock")
            return render(request, self.template_name, self.build_context(manual_form=manual_form))

        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            stock = form.save()
            messages.success(request, f"Stock mis à jour pour {stock.item_name}.")
            push_low_stock_messages(request)
            return redirect("stock")

        return render(request, self.template_name, self.build_context(form=form))


class SetListView(View):
    template_name = "core/set_list.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        ensure_stock_records()
        sets = Set.objects.all()
        context = {
            "set_rows": [
                {
                    "set": set_obj,
                    "cost": set_obj.fabrication_cost(),
                    "possible": set_obj.max_producible(),
                    "low_stock": set_obj.max_producible() <= 2,
                }
                for set_obj in sets
            ]
        }
        return render(request, self.template_name, context)


class SetDetailView(View):
    template_name = "core/set_detail.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        ensure_stock_records()
        set_obj = get_object_or_404(Set, pk=pk)
        low_ids = {item.pk for item in set_obj.low_stock_items()}
        tool_rows = []
        consumable_rows = []
        for item in set_obj.items.select_related("tool", "consumable"):
            stock = Stock.objects.filter(tool=item.tool).first() if item.tool_id else Stock.objects.filter(consumable=item.consumable).first()
            row = {
                "item": item,
                "stock": stock.current_quantity if stock else Decimal("0.00"),
                "is_low": item.pk in low_ids,
            }
            if item.tool_id:
                tool_rows.append(row)
            else:
                consumable_rows.append(row)
        context = {
            "set_obj": set_obj,
            "tool_rows": tool_rows,
            "consumable_rows": consumable_rows,
            "cost": set_obj.fabrication_cost(),
            "possible": set_obj.max_producible(),
        }
        return render(request, self.template_name, context)


class ProductionView(View):
    template_name = "core/production.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        ensure_stock_records()
        return render(request, self.template_name, {"form": ProductionForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        ensure_stock_records()
        form = ProductionForm(request.POST)
        if form.is_valid():
            set_obj = form.cleaned_data["set"]
            quantity = form.cleaned_data["quantity"]
            with transaction.atomic():
                for item in set_obj.items.select_related("consumable"):
                    if not item.consumable_id:
                        continue
                    stock = Stock.objects.get(consumable=item.consumable)
                    stock.add_quantity(-(item.required_quantity * quantity))
            messages.success(request, f"Production validée pour {quantity} set(s) {set_obj.name}.")
            push_low_stock_messages(request)
            return redirect("production")
        return render(request, self.template_name, {"form": form})
