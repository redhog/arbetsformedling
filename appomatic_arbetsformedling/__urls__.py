import django.conf.urls
import appomatic_arbetsformedling.forms

urlpatterns = django.conf.urls.patterns('',
    (r'^skill/?$', 'appomatic_arbetsformedling.views.skills'),
    (r'^skill/create?$', 'appomatic_arbetsformedling.views.skill_create'),
    (r'^skill/(?P<name>.*)/?$', 'appomatic_arbetsformedling.views.skill'),
    (r'^project/?$', 'appomatic_arbetsformedling.views.projects'),
    (r'^project/create/?$', 'appomatic_arbetsformedling.views.project_create'),
    (r'^project/(?P<name>.*)/edit/?$', 'appomatic_arbetsformedling.views.project_edit'),
    (r'^project/(?P<name>.*)/signup/?$', 'appomatic_arbetsformedling.views.project_signup'),
    (r'^project/(?P<name>.*)/signdown/?$', 'appomatic_arbetsformedling.views.project_signdown'),
    (r'^project/(?P<name>.*)/?$', 'appomatic_arbetsformedling.views.project'),


    # Edit profile
    django.conf.urls.url(r'^accounts/(?P<username>[\.\w-]+)/edit/$',
     'userena.views.profile_edit',
     name='userena_profile_edit',
     kwargs={"edit_profile_form": appomatic_arbetsformedling.forms.EditProfileForm}
    ),
)
