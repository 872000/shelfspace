"""Server-rendered UI tests for ShelfSpace."""
from datetime import date, timedelta

import pytest
from django.urls import reverse

from library.models import Book, Loan, ReadingLog


@pytest.mark.django_db
class TestUi:
    def test_dashboard_loads_with_stats(self, client):
        Book.objects.create(title="Dune", author="Frank Herbert")
        ReadingLog.objects.create(date=date.today(), pages=20)
        resp = client.get(reverse("library:dashboard"))
        assert resp.status_code == 200
        assert b"Dune" in resp.content
        assert b"day streak" in resp.content

    def test_dashboard_shows_overdue(self, client):
        book = Book.objects.create(title="Late Book")
        Loan.objects.create(book=book, friend_name="Sam",
                            due_at=date.today() - timedelta(days=3))
        resp = client.get(reverse("library:dashboard"))
        assert resp.status_code == 200
        assert b"Overdue returns" in resp.content

    def test_add_book_by_isbn_creates_book(self, client):
        resp = client.post(reverse("library:book_add_isbn"),
                           {"isbn": "978-0-14-143951-8"})
        assert resp.status_code == 302
        assert Book.objects.filter(title="Pride and Prejudice").exists()

    def test_add_book_by_unknown_isbn_stays_on_page(self, client):
        resp = client.post(reverse("library:book_add_isbn"),
                           {"isbn": "9780000000000"})
        assert resp.status_code == 200
        assert Book.objects.count() == 0

    def test_lend_book_from_detail_page(self, client):
        book = Book.objects.create(title="Dune")
        resp = client.post(reverse("library:book_detail", args=[book.pk]), {
            "action": "lend", "friend_name": "Sam",
            "due_at": str(date.today() + timedelta(days=14)),
        })
        assert resp.status_code == 302
        book.refresh_from_db()
        assert book.active_loan.friend_name == "Sam"

    def test_cannot_double_lend_from_detail_page(self, client):
        book = Book.objects.create(title="Dune")
        Loan.objects.create(book=book, friend_name="Sam",
                            due_at=date.today() + timedelta(days=14))
        resp = client.post(reverse("library:book_detail", args=[book.pk]), {
            "action": "lend", "friend_name": "Alex",
            "due_at": str(date.today() + timedelta(days=7)),
        })
        assert resp.status_code == 200  # form re-rendered with the error
        assert Loan.objects.filter(book=book).count() == 1

    def test_log_reading_from_detail_page(self, client):
        book = Book.objects.create(title="Dune")
        resp = client.post(reverse("library:book_detail", args=[book.pk]), {
            "action": "log", "date": str(date.today()), "pages": 25,
            "book": book.pk,
        })
        assert resp.status_code == 302
        assert ReadingLog.objects.filter(pages=25).exists()

    def test_mark_finished_from_detail_page(self, client):
        book = Book.objects.create(title="Dune", status=Book.Status.READING)
        resp = client.post(reverse("library:book_detail", args=[book.pk]),
                           {"action": "finish"})
        assert resp.status_code == 302
        book.refresh_from_db()
        assert book.status == Book.Status.FINISHED
        assert book.date_finished == date.today()

    def test_return_loan_from_loan_list(self, client):
        book = Book.objects.create(title="Dune")
        loan = Loan.objects.create(book=book, friend_name="Sam",
                                   due_at=date.today() + timedelta(days=7))
        resp = client.get(reverse("library:loan_return", args=[loan.pk]))
        assert resp.status_code == 302
        loan.refresh_from_db()
        assert loan.returned_at == date.today()

    def test_book_list_filter(self, client):
        Book.objects.create(title="A", status=Book.Status.FINISHED)
        Book.objects.create(title="B", status=Book.Status.TO_READ)
        resp = client.get(reverse("library:book_list") + "?status=finished")
        assert resp.status_code == 200
        assert b">A<" in resp.content
        assert b">B<" not in resp.content
