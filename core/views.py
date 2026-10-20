from itertools import groupby

from django.views.generic import DetailView, ListView, TemplateView

from .models import AboutPage, Category, Project, ProjectsPage


SLIDER_LIMIT = 8  # больше слайдов в ленте-указателе не помещается


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # слайдер вверху главной: проекты с галочкой «Показывать в слайдере на главной»
        ctx["slider_projects"] = list(
            Project.objects.filter(is_published=True, show_in_slider=True).exclude(cover="")[:SLIDER_LIMIT])
        ctx["home_projects"] = list(Project.objects.filter(is_published=True, show_on_home=True)[:6])
        return ctx


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["about"] = AboutPage.load()
        return ctx


class ProjectListView(ListView):
    template_name = "projects.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        qs = Project.objects.filter(is_published=True)
        cats = [c for c in self.request.GET.getlist("category") if c]
        if cats:
            qs = qs.filter(categories__slug__in=cats).distinct()  # проект подходит, если есть любая из выбранных категорий
        year = self.request.GET.get("year", "")
        if year.isdigit():
            qs = qs.filter(year=int(year))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        get = self.request.GET
        selected = [c for c in get.getlist("category") if c]
        year = get.get("year", "")
        page_obj = ctx.get("page_obj")
        next_url = ""
        if page_obj and page_obj.has_next():
            q = get.copy()
            q["page"] = str(page_obj.next_page_number())
            next_url = "?" + q.urlencode()
        published = Project.objects.filter(is_published=True)
        ctx.update({
            "projects_page": ProjectsPage.load(),
            "categories": Category.objects.filter(projects__is_published=True).distinct(),
            "years": sorted(set(published.exclude(year__isnull=True).values_list("year", flat=True)), reverse=True),
            "selected_categories": set(selected),
            "selected_year": year,
            "has_filters": bool(selected or year),
            "next_url": next_url,
        })
        return ctx


class ProjectDetailView(DetailView):
    template_name = "project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(is_published=True).prefetch_related("items")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        rows = []
        for number, group in groupby(self.object.items.all(), key=lambda i: i.row):
            group = list(group)
            full = next((i for i in group if i.kind == "image" and i.full_bleed and i.image), None)
            rows.append({
                "number": number,
                "space": group[0].space,
                "full": full,
                "items": [i for i in group if i is not full],
            })
        ctx["rows"] = rows
        return ctx


class ContactsView(TemplateView):
    template_name = "contacts.html"
