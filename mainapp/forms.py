from django import forms
from .models import TaskCard


class TaskCardForm(forms.ModelForm):

    class Meta:
        model = TaskCard
        fields = ('text',)