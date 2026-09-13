from django import forms
from django.db.models import Q
from .models import TrainingBlock, TrainingProgram, ProgramBlock


class TrainingBlockForm(forms.ModelForm):
    class Meta:
        model  = TrainingBlock
        fields = ['title', 'sport', 'kind', 'duration_min', 'equipment', 'description', 'scheme']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }

class TrainingProgramForm(forms.ModelForm):
    class Meta:
        model  = TrainingProgram
        fields = ['title', 'sport', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class ProgramBlockForm(forms.ModelForm):
    class Meta:
        model  = ProgramBlock
        fields = ['block', 'session', 'order']

    def __init__(self, *args, program=None, **kwargs):
        super().__init__(*args, **kwargs)
        if program is not None:
            # В программу можно добавить блоки её секции и общие
            self.fields['block'].queryset = TrainingBlock.objects.filter(
                Q(sport=program.sport) | Q(sport__isnull=True)
            )