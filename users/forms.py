from django.contrib.auth.forms import UserCreationForm
from django.forms import TextInput, PasswordInput, EmailInput


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)
        widgets = {
            "username": TextInput(attrs={"placeholder": "Your username"}),
            "password1": PasswordInput(attrs={"placeholder": "Enter a password"}),
            "password2": PasswordInput(attrs={"placeholder": "Enter a password"}),
            "email": EmailInput(attrs={"placeholder": "Your Email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, widget in self.Meta.widgets.items():
            if field_name in self.fields:
                self.fields[field_name].widget = widget
