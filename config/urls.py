from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

admin.site.site_header = "Coloroom Interiors"
admin.site.site_title = "Coloroom Interiors"
admin.site.index_title = "Управление сайтом"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Предпросмотр страницы 404 при DEBUG=1 (в боевом режиме Django сам покажет templates/404.html)
    urlpatterns += [path("preview-404/", TemplateView.as_view(template_name="404.html"))]
