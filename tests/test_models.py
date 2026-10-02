"""Model tests for ShelfSpace."""
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from library.models import Book, Loan, ReadingLog


@pytest.mark.django_db
class TestBook:
    def test_str(self):
        b = Book.objects.create(title="Dune", author="Frank Herbert")
        assert str(b) == "Dune by Frank Herbert"

    def test_str_without_author(self):
        b = Book.objects.create(title="Anonymous")
        assert str(b) == "Anonymous"

    def test_isbn_normalized_on_save(self):
        b = Book.objects.create(title="T", isbn="978-0-14-143951-8")
        assert b.isbn == "9780141439518"

    def test_default_status_is_to_read(self):
        b = Book.objects.create(title="T")
        assert b.status == Book.Status.TO_READ

    def test_is_available_when_not_lent(self):
        b = Book.objects.create(title="T")
        assert b.is_available is True


@pytest.mark.django_db
class TestLoan:
    def test_lend_and_return(self):
        b = Book.objects.create(title="Dune")
        loan = Loan.objects.create(book=b, friend_name="Sam",
                                   due_at=date.today() + timedelta(days=14))
        assert b.is_available is False
        loan.returned_at = date.today()
        loan.save()
        assert b.is_available is True

    def test_cannot_lend_already_lent_book(self):
        b = Book.objects.create(title="Dune")
        Loan.objects.create(book=b, friend_name="Sam",
                            due_at=date.today() + timedelta(days=14))
        with pytest.raises(ValidationError):
            Loan.objects.create(book=b, friend_name="Alex",
                                due_at=date.today() + timedelta(days=7))

    def test_can_relend_after_return(self):
        b = Book.objects.create(title="Dune")
        first = Loan.objects.create(book=b, friend_name="Sam",
                                    due_at=date.today() + timedelta(days=14))
        first.returned_at = date.today()
        first.save()
        second = Loan.objects.create(book=b, friend_name="Alex",
                                     due_at=date.today() + timedelta(days=7))
        assert second.pk is not None

    def test_is_overdue(self):
        b = Book.objects.create(title="Dune")
        late = Loan(book=b, friend_name="Sam",
                    due_at=date.today() - timedelta(days=1))
        assert late.is_overdue() is True
        on_time = Loan(book=b, friend_name="Sam",
                       due_at=date.today() + timedelta(days=1))
        assert on_time.is_overdue() is False


@pytest.mark.django_db
class TestReadingLog:
    def test_str(self):
        log = ReadingLog.objects.create(date=date(2026, 1, 5), pages=42)
        assert str(log) == "2026-01-05: 42 pages"

    def test_date_unique(self):
        ReadingLog.objects.create(date=date(2026, 1, 5), pages=10)
        with pytest.raises(IntegrityError):
            ReadingLog.objects.create(date=date(2026, 1, 5), pages=20)
