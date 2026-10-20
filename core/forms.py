from django import forms

from .models import ContactRequest


class ContactRequestForm(forms.ModelForm):
    # Скрытое поле-ловушка для спам-ботов: человек его не заполняет.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={
        "tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = ContactRequest
        fields = ("name", "phone", "email", "message")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ваше имя", "autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"placeholder": "+998", "autocomplete": "tel", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com", "autocomplete": "email"}),
            "message": forms.Textarea(attrs={"placeholder": "Расскажите о задаче: тип объекта, площадь, сроки", "rows": 5}),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam")
        return ""
