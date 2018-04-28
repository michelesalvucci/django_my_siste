from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from datetime import date
from datetime import timedelta

# Model form
from django.forms import ModelForm

from .models import BookInstance


class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
        """
            Come nella Form normale
            Il nome e' due_back anziche' renewal perche' arriava dal field del model
        """
        data = self.cleaned_data['due_back']

        # Check date is not in past.
        if data < date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check date is in range librarian allowed to change (+4 weeks)
        if data > date.today() + timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data

    class Meta:
        model = BookInstance
        fields = ['due_back',]

        # Override dei widget
        labels = {'due_back': _('Renewal date'), }
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).'), }


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check date is not in past.
        if data < date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check date is in range librarian allowed to change (+4 weeks).
        if data > date.today() + timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # Remember to always return the cleaned data.
        return data