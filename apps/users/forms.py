# apps/users/forms.py
from django import forms
from apps.users.models import User
from apps.roles.models import Role


class UserCreateForm(forms.ModelForm):
    """
    Used by system admins to create new users.
    - first_name, middle_name, last_name stored
    - superuser / is_staff hidden (auto-set by view based on user_type)
    - Single role selection via RadioSelect (one role per user at creation)
    """
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
    )
    middle_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Middle Name (optional)'}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        min_length=8,
    )
    password_confirm = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        label='Assign Role',
        empty_label='- No role -',
        widget=forms.RadioSelect,
    )

    class Meta:
        model  = User
        # Note: is_staff / is_superuser intentionally excluded; auto-set in view
        fields = ['first_name', 'middle_name', 'last_name', 'username', 'email', 'user_type', 'is_active']
        widgets = {
            'username':  forms.TextInput(attrs={'placeholder': 'Username'}),
            'email':     forms.EmailInput(attrs={'placeholder': 'Email'}),
            'user_type': forms.Select(),
            'is_active': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Refresh role queryset in case roles have changed
        self.fields['role'].queryset = Role.objects.all().order_by('display_name')

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password_confirm'):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class UserEditForm(forms.ModelForm):
    """
    Edit an existing user.
    - Name fields included
    - Single role selection
    - is_staff excluded (auto-managed)
    """
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
    )
    middle_name = forms.CharField(
        max_length=150, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Middle Name (optional)'}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
    )
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        label='Assign Role',
        empty_label='- No role -',
        widget=forms.RadioSelect,
    )

    class Meta:
        model  = User
        fields = ['first_name', 'middle_name', 'last_name', 'username', 'email', 'user_type', 'is_active']
        widgets = {
            'username':  forms.TextInput(attrs={'placeholder': 'Username'}),
            'email':     forms.EmailInput(attrs={'placeholder': 'Email'}),
            'user_type': forms.Select(),
            'is_active': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].queryset = Role.objects.all().order_by('display_name')
        # Pre-select current role (first role if multiple exist)
        if self.instance and self.instance.pk:
            current_role = self.instance.user_roles.select_related('role').first()
            if current_role:
                self.fields['role'].initial = current_role.role
            # Populate name fields from instance
            self.fields['middle_name'].initial = self.instance.middle_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class AdminPasswordChangeForm(forms.Form):
    """Allow a system admin to change their own password from their profile."""
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Current Password'}),
    )
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}),
        min_length=8,
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if not self.user.check_password(current):
            raise forms.ValidationError("Current password is incorrect.")
        return current

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('new_password') != cleaned.get('confirm_password'):
            raise forms.ValidationError("New passwords do not match.")
        return cleaned