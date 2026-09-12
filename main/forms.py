from django import forms

from .models import TrainingBlock


class TrainingBlockForm(forms.ModelForm):
    class Meta:
        model  = TrainingBlock
        fields = ['title', 'sport', 'kind', 'duration_min', 'equipment', 'description', 'scheme']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }