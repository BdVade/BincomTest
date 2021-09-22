from django.forms import ModelForm
from .models import AnnouncedPuResults


class ResultUploadForm(ModelForm):
    class Meta:
        model = AnnouncedPuResults
        fields = ['polling_unit_uniqueid', 'party_abbreviation', 'party_score', 'entered_by_user']
