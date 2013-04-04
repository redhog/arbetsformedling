import autocomplete_light
autocomplete_light.autodiscover()

from django.conf.urls import patterns, include

urlpatterns = patterns(
    '',
   (r'^autocomplete/', include('autocomplete_light.urls')),
)
