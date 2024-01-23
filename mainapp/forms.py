from django import forms
from .models import TaskCard
from django.contrib.auth.models import User


class TaskCardForm(forms.ModelForm):

    class Meta:
        model = TaskCard
        fields = ('text',)


class SetExecutorForm(forms.ModelForm):
    
    class Meta:
        model = TaskCard
        fields = ['executor'] 

    def __init__(self, user, *args, **kwargs):
        super(SetExecutorForm, self).__init__(*args, **kwargs)
        self.user = user
        if self.user.is_superuser:
            self.fields['executor'].queryset = User.objects.all()
        else:
            self.fields['executor'].queryset = User.objects.filter(id=self.user.id)

