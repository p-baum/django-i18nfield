import django
import json
from django.conf import settings
from django.db import models

from .forms import I18nFormField, I18nTextarea, I18nTextInput
from .strings import LazyI18nString


class I18nField(models.JSONField):
    form_class = I18nFormField
    widget = I18nTextInput

    def to_python(self, value):
        if isinstance(value, LazyI18nString):
            return value
        if value is None:
            return None
        return LazyI18nString(value)

    def get_prep_value(self, value):
        if isinstance(value, LazyI18nString):
            value = value.data
        if isinstance(value, dict):
            return json.dumps({k: v for k, v in value.items() if v}, sort_keys=True)
        if isinstance(value, LazyI18nString.LazyGettextProxy):
            return json.dumps({lng: value[lng] for lng, lngname in settings.LANGUAGES if value[lng]}, sort_keys=True)
        return value

    # def get_prep_lookup(self, lookup_type, value):  # NOQA
    #     raise TypeError('Lookups on i18n strings are currently not supported.')

    # def get_prep_lookup(self):
    #     return [str(item) for item in self.rhs]
    
    def from_db_value(self, value, expression, connection):
        value = super().from_db_value(value, expression, connection)
        return LazyI18nString(value)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        defaults = {'form_class': self.form_class, 'widget': self.widget}
        return super().formfield(defaults | kwargs)


