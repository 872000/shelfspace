"""Tests for reading statistics."""
from datetime import date, timedelta

import pytest

from library import stats
from library.models import Book, Loan, ReadingLog


@pytest.mark.django_db
class TestStats:
    def test_books_finished_this_month(self):
        today = date.today()
        Book.objects.create(title="A", status=Book.Status.FINISHED,
                            date_finished=today)
        Book.objects.create(title="B", status=Book.Status.FINISHED,
                            date_finished=today - timedelta(days=60))
        Book.objects.create(title="C", status=Book.Status.READING)
        assert stats.books_finished_this_month() == 1

    def test_books_finished_by_month_shape(self):
        rows = stats.books_finished_by_month(months=3)
        assert len(rows) == 3
        assert all("books_finished" in r for r in rows)
        # months are in ascending order
        assert [(r["year"], r["month"]) for r in rows] == sorted(
            (r["year"], r["month"]) for r in rows)

    def test_total_pages_read(self):
        ReadingLog.objects.create(date=date.today(), pages=30)
        ReadingLog.objects.create(date=date.today() - timedelta(days=1), pages=20)
        assert stats.total_pages_read() == 50

    def test_total_pages_read_empty(self):
        assert stats.total_pages_read() == 0

    def test_current_streak_counts_consecutive_days(self):
        today = date.today()
        for i in range(4):
            ReadingLog.objects.create(date=today - timedelta(days=i), pages=10)
        assert stats.current_streak() == 4

    def test_current_streak_tolerates_missing_today(self):
        today = date.today()
        for i in range(1, 3):
            ReadingLog.objects.create(date=today - timedelta(days=i), pages=10)
        assert stats.current_streak() == 2

    def test_current_streak_breaks_on_gap(self):
        today = date.today()
        ReadingLog.objects.create(date=today, pages=10)
        ReadingLog.objects.create(date=today - timedelta(days=2), pages=10)
        assert stats.current_streak() == 1

    def test_current_streak_zero_when_nothing_logged(self):
        assert stats.current_streak() == 0

    def test_overdue_loans(self):
        b1 = Book.objects.create(title="Late")
        b2 = Book.objects.create(title="OnTime")
        b3 = Book.objects.create(title="ReturnedLate")
        Loan.objects.create(book=b1, friend_name="Sam",
                            due_at=date.today() - timedelta(days=2))
        Loan.objects.create(book=b2, friend_name="Alex",
                            due_at=date.today() + timedelta(days=5))
        late = Loan.objects.create(book=b3, friend_name="Jo",
                                   due_at=date.today() - timedelta(days=9))
        late.returned_at = date.today()
        late.save()
        overdue = stats.overdue_loans()
        assert list(overdue.values_list("book__title", flat=True)) == ["Late"]

    def test_summary_keys(self):
        s = stats.summary()
        for key in ("total_books", "books_finished_this_month", "total_pages_read",
                    "current_streak_days", "books_lent_out", "overdue_loans",
                    "monthly"):
            assert key in s
