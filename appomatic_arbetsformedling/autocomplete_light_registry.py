import autocomplete_light
import appomatic_arbetsformedling.models

autocomplete_light.register(
    appomatic_arbetsformedling.models.Skill,
    search_fields=['name'],
    add_another_url_name='appomatic_arbetsformedling.views.skill_create')
