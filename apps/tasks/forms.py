from django import forms
from apps.tasks.models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = []
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'e.g. moderator',
                'class': 'form-control',
            }),
            'display_name': forms.TextInput(attrs={
                'placeholder': 'e.g. Moderator',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Short description of this role...',
                'class': 'form-control',
                'rows': 3,
            }),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip().lower().replace(' ', '_')
        qs = Role.objects.filter(name=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A role with this name already exists.")
        return name

    def clean(self):
        cleaned = super().clean()
        # If marking as default, warn that other default will be unset
        # (handle this in view or signal if needed)
        return cleaned