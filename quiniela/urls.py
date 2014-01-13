from django.conf.urls import patterns, include, url
from quiniela.core import views
from quiniela.core.views import Principal

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    #url(r'^$', Inicio.as_view(), name='inicio'),
    url(r'^main/$', Principal.as_view(), name='principal'),
    url(r'^new_jornada/$', views.crear_jornada, name='crear_jornada'),
    url(r'^new_apuesta/$', views.crear_apuesta, name='crear_apuesta'),
    #url(r'^new_apuesta/$', CrearApuesta.as_view(), name='crear_apuesta'),
    url(r'^$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}),
    # url(r'^quiniela/', include('quiniela.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
