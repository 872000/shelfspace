"""API tests for ShelfSpace."""
from datetime import date, timedelta

import pytest

from library.models import Book, Loan, ReadingLog


@pytest.mark.django_db
class TestBookApi:
    def test_create_and_list_books(self, client):
        resp = client.post("/api/books/", {
            "title": "Dune", "author": "Frank Herbert",
            "pages": 412, "status": "reading",
        }, content_type="application/json")
        assert resp.status_code == 201
        resp = client.get("/api/books/")
        assert resp.status_code == 200
        assert any(b["title"] == "Dune" for b in resp.json())


@pytest.mark.django_db
class TestIsbnApi:
    def test_known_isbn(self, client):
        resp = client.get("/api/isbn/", {"isbn": "978-0-14-081774-4"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "1984"
        assert resp.json()["found"] is True

    def test_unknown_isbn_404(self, client):
        resp = client.get("/api/isbn/", {"isbn": "9780000000000"})
        assert resp.status_code == 404
        assert resp.json()["found"] is False


@pytest.mark.django_db
class TestLoanApi:
    def test_lend_return_and_overdue(self, client):
        book = Book.objects.create(title="Dune")
        resp = client.post("/api/loans/", {
            "book": book.pk, "friend_name": "Sam",
            "due_at": str(date.today() - timedelta(days=1)),
        }, content_type="application/json")
        assert resp.status_code == 201
        loan_id = resp.json()["id"]

        # double-lend is rejected
        resp = client.post("/api/loans/", {
            "book": book.pk, "friend_name": "Alex",
            "due_at": str(date.today() + timedelta(days=7)),
        }, content_type="application/json")
        assert resp.status_code == 400

        # shows up as overdue
        resp = client.get("/api/loans/overdue/")
        assert resp.status_code == 200
        assert any(l["id"] == loan_id for l in resp.json())

        # return it
        resp = client.post(f"/api/loans/{loan_id}/mark_returned/")
        assert resp.status_code == 200
        assert resp.json()["returned_at"] is not None

        # returning twice is rejected
        resp = client.post(f"/api/loans/{loan_id}/mark_returned/")
        assert resp.status_code == 400


@pytest.mark.django_db
class TestReadingLogApi:
    def test_create_log(self, client):
        book = Book.objects.create(title="Dune")
        resp = client.post("/api/reading-logs/", {
            "date": str(date.today()), "pages": 35, "book": book.pk,
        }, content_type="application/json")
        assert resp.status_code == 201


@pytest.mark.django_db
class TestStatsApi:
    def test_stats_endpoint(self, client):
        Book.objects.create(title="Dune")
        resp = client.get("/api/stats/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_books"] == 1
        assert "current_streak_days" in data
        assert len(data["monthly"]) == 6
