from django import forms
from django.contrib import admin
from django.db.models import Max
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.utils.text import slugify
from unfold.admin import ModelAdmin, TabularInline

from .models import (AboutPage, Category, ContactBlock, ContactRequest, MenuItem, Project,
                     ProjectItem, ProjectsPage, SiteSettings)


class SingletonAdmin(ModelAdmin):
    """Список не нужен: сразу открываем единственную запись."""

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.load()
        info = self.model._meta.app_label, self.model._meta.model_name
        return redirect(reverse("admin:%s_%s_change" % info, args=[obj.pk]))


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ("Основное", {"fields": ("site_name", "meta_description", "logo")}),
        ("Баннеры", {"fields": ("hero_image", "service_banner"),
                     "description": "Баннер на главной показывается, пока ни один проект не отмечен "
                                    "галочкой «Показывать в слайдере на главной»."}),
        ("Блок «О нас»", {"fields": ("about_title", "about_note", "about_short", "about_image_small", "about_image", "about_button")}),
        ("Блок «Проекты»", {"fields": ("projects_title", "projects_note", "projects_middle_text", "projects_button")}),
        ("Подвал", {"fields": ("footer_right_title", "footer_bg", "copyright_text")}),
        ("Страница «Контакты»", {"fields": ("footer_left_title",)}),
    )


@admin.register(AboutPage)
class AboutPageAdmin(SingletonAdmin):
    fieldsets = (
        ("Баннер и вступление", {"fields": ("title", "banner", "lead", "body")}),
        ("Фото и крупная фраза", {"fields": ("image", "statement")}),
        ("Блок «Философия»", {"fields": ("philosophy_title", "philosophy_text", "philosophy_image")}),
        ("Блок «Команда»", {"fields": ("team_title", "team_text", "team_image")}),
    )


@admin.register(ProjectsPage)
class ProjectsPageAdmin(SingletonAdmin):
    fields = ("title", "banner", "intro", "load_more_label")


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MenuItem)
class MenuItemAdmin(ModelAdmin):
    list_display = ("title", "page", "custom_url", "order", "is_active")
    list_display_links = ("title",)
    list_editable = ("order", "is_active")
    ordering = ("order", "id")


_TRANSLIT = dict(zip(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
     "f", "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "yu", "ya"],
))


def make_category_slug(name):
    """Адресный код категории из русского названия: «Жилые» -> zhilye (с защитой от повторов)."""
    base = slugify("".join(_TRANSLIT.get(ch, ch) for ch in name.lower())) or "category"
    slug, i = base, 2
    while Category.objects.filter(slug=slug).exists():
        slug, i = f"{base}-{i}", i + 1
    return slug


class ProjectAdminForm(forms.ModelForm):
    new_categories = forms.CharField(
        label="Новые категории", required=False,
        help_text="Если нужной категории нет в списке, впишите её здесь (несколько — через запятую). "
                  "Она будет создана, отмечена у этого проекта и появится в фильтре на странице «Проекты».",
    )

    class Meta:
        model = Project
        fields = "__all__"
        widgets = {"categories": forms.CheckboxSelectMultiple}


class ProjectItemInline(TabularInline):
    model = ProjectItem
    extra = 1
    fields = ("row", "kind", "image", "text", "col_start", "col_span", "align", "space", "full_bleed", "light_text", "bring_to_front")
    verbose_name = "элемент страницы"
    verbose_name_plural = "Содержимое страницы проекта (фото и тексты по рядам)"


@admin.register(Project)
class ProjectAdmin(ModelAdmin):
    list_display = ("thumb", "title", "subtitle", "year", "is_published", "show_on_home", "show_in_slider", "order")
    list_display_links = ("thumb", "title")
    list_editable = ("is_published", "show_on_home", "show_in_slider", "order")
    list_filter = ("is_published", "show_on_home", "show_in_slider", "categories")
    search_fields = ("title", "subtitle", "location")
    prepopulated_fields = {"slug": ("title", "subtitle")}
    form = ProjectAdminForm
    inlines = [ProjectItemInline]
    fieldsets = (
        ("Карточка проекта", {"fields": ("title", "subtitle", "slug", "cover", "short_description")}),
        ("Шапка страницы проекта", {"fields": ("banner", "plan_image", "project_type", "location", "status",
                                               "year", "plot_area", "area", "team")}),
        ("Категории (для фильтров на странице «Проекты»)", {"fields": ("categories", "new_categories")}),
        ("Публикация", {"fields": ("is_published", "show_on_home", "show_in_slider", "order")}),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        names = [n.strip() for n in (form.cleaned_data.get("new_categories") or "").split(",") if n.strip()]
        if not names:
            return
        next_order = (Category.objects.aggregate(m=Max("order"))["m"] or 0) + 1
        for name in names:
            cat = Category.objects.filter(name__iexact=name).first()
            if not cat:
                cat = Category.objects.create(name=name, slug=make_category_slug(name), order=next_order)
                next_order += 1
            form.instance.categories.add(cat)

    @admin.display(description="Обложка")
    def thumb(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" style="width:56px;height:56px;object-fit:cover;border-radius:6px">',
                obj.cover.url,
            )
        return "—"


@admin.register(ContactBlock)
class ContactBlockAdmin(ModelAdmin):
    list_display = ("label", "column", "show_in_footer", "order")
    list_editable = ("show_in_footer", "order")
    list_filter = ("column",)


@admin.register(ContactRequest)
class ContactRequestAdmin(ModelAdmin):
    list_display = ("name", "phone", "email", "created_at", "is_processed")
    list_editable = ("is_processed",)
    list_filter = ("is_processed", "created_at")
    search_fields = ("name", "phone", "email", "message")
    readonly_fields = ("created_at",)
