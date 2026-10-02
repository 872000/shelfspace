"""ShelfSpace models: books, loans and daily reading logs."""
from django.core.exceptions import ValidationError
from django.db import models


class Book(models.Model):
    class Status(models.TextChoices):
        TO_READ = "to_read", "To read"
        READING = "reading", "Reading"
        FINISHED = "finished", "Finished"

    title = models.CharField(max_length=250)
    author = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=20, blank=True,
                            help_text="Digits only; dashes are stripped on save")
    pages = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices,
                              default=Status.TO_READ)
    date_added = models.DateField(auto_now_add=True)
    date_finished = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} by {self.author}" if self.author else self.title

    def save(self, *args, **kwargs):
        self.isbn = "".join(ch for ch in self.isbn if ch.isdigit() or ch.lower() == "x")
        super().save(*args, **kwargs)

    @property
    def active_loan(self):
        return self.loans.filter(returned_at__isnull=True).first()

    @property
    def is_available(self):
        return self.active_loan is None


class Loan(models.Model):
    """One lending of a book to a friend."""

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="loans")
    friend_name = models.CharField(max_length=120)
    lent_at = models.DateField(auto_now_add=True)
    due_at = models.DateField()
    returned_at = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["due_at"]

    def __str__(self):
        return f"{self.book.title} -> {self.friend_name}"

    def clean(self):
        # book may not be assigned yet when this runs during ModelForm
        # validation (the form sets it afterwards), so guard on book_id.
        if self.returned_at is None and self.pk is None and self.book_id:
            if self.book.loans.filter(returned_at__isnull=True).exists():
                raise ValidationError(
                    f'"{self.book.title}" is already lent out and not yet returned.')

    def save(self, *args, **kwargs):
        self.full_clean(exclude=["lent_at"])
        super().save(*args, **kwargs)

    def is_overdue(self, today=None):
        from datetime import date
        today = today or date.today()
        return self.returned_at is None and self.due_at < today


class ReadingLog(models.Model):
    """Pages read on a given day (drives streaks and totals)."""

    date = models.DateField(unique=True)
    pages = models.PositiveIntegerField()
    book = models.ForeignKey(Book, on_delete=models.SET_NULL,
                             null=True, blank=True, related_name="reading_logs")

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.date:%Y-%m-%d}: {self.pages} pages"
