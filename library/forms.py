from django import forms

from .models import Book, Loan, ReadingLog


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "isbn", "pages", "status"]


class ISBNLookupForm(forms.Form):
    isbn = forms.CharField(max_length=20, label="ISBN",
                           help_text="Looked up offline in the bundled catalog")


class LoanForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ["friend_name", "due_at", "notes"]
        widgets = {"due_at": forms.DateInput(attrs={"type": "date"})}


class ReadingLogForm(forms.ModelForm):
    class Meta:
        model = ReadingLog
        fields = ["date", "pages", "book"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}
