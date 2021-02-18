
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path
from app import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('database', views.database, name='database'),
    path('analyze', views.analyze, name='analyze'),
    path('status/<slug:status_hash>', views.status, name='status'),
    path('diffcoexp/<int:id>/', views.diffcoexp, name='diffcoexp'),
    path('network/<int:id>/<int:type_id>', views.network, name='network'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

