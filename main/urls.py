import warnings

from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin
from django.views.static import serve as serve_static
from django.contrib.auth import views as authviews

warnings.simplefilter("error", DeprecationWarning)

from pjtk2.views import project_list

admin.autodiscover()

urlpatterns = [
    url(r"^$", project_list, name="home"),
    url(r"^$", project_list, name="index"),
    url(r"^admin/doc/", include("django.contrib.admindocs.urls")),
    url(r"^coregonusclupeaformis/admin/", admin.site.urls),
    url(r"^accounts/", include("django.contrib.auth.urls")),
    url(
        "^accounts/password-change/$",
        authviews.PasswordChangeView.as_view(),
        name="change_password",
    ),
    url(
        "^accounts/password-change/done/$",
        authviews.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
    url(r"^projects/", include("pjtk2.urls")),
    url(
        r"^static/(?P<path>.*)$", serve_static, {"document_root": settings.STATIC_ROOT}
    ),
    url(
        r"^uploads/(?P<path>.*)$", serve_static, {"document_root": settings.MEDIA_ROOT}
    ),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [url(r"^__debug__/", include(debug_toolbar.urls))] + urlpatterns
