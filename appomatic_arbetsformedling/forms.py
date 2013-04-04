import appomatic_arbetsformedling.models
import django.forms
import autocomplete_light
from django.utils.translation import ugettext_lazy as _

class EditProfileForm(django.forms.ModelForm):
    """ Base form used for fields that are always required """
    first_name = django.forms.CharField(label=_(u'First name'),
                                        max_length=30,
                                        required=False)
    last_name = django.forms.CharField(label=_(u'Last name'),
                                       max_length=30,
                                       required=False)

    def __init__(self, *args, **kw):
        super(EditProfileForm, self).__init__(*args, **kw)
        # Put the first and last name at the top
        new_order = self.fields.keyOrder[:-2]
        new_order.insert(0, 'first_name')
        new_order.insert(1, 'last_name')
        self.fields.keyOrder = new_order

    class Meta:
        model = appomatic_arbetsformedling.models.Profile
        exclude = ['user']
        widgets = autocomplete_light.get_widgets_dict(appomatic_arbetsformedling.models.Profile)

    def save(self, force_insert=False, force_update=False, commit=True):
        profile = super(EditProfileForm, self).save(commit=commit)
        # Save first and last name
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        return profile
