"""Reading statistics for ShelfSpace."""
from datetime import date, timedelta

from django.db.models import Sum

from .models import Book, Loan, ReadingLog


def books_finished_this_month(today: date | None = None) -> int:
    today = today or date.today()
    return Book.objects.filter(
        status=Book.Status.FINISHED,
        date_finished__year=today.year,
        date_finished__month=today.month,
    ).count()


def books_finished_by_month(months: int = 6, today: date | None = None) -> list[dict]:
    """Finished-book counts for the last N months, oldest first."""
    today = today or date.today()
    out = []
    year, month = today.year, today.month
    for _ in range(months):
        count = Book.objects.filter(
            status=Book.Status.FINISHED,
            date_finished__year=year,
            date_finished__month=month,
        ).count()
        out.append({"year": year, "month": month, "books_finished": count})
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    return list(reversed(out))


def total_pages_read() -> int:
    return ReadingLog.objects.aggregate(total=Sum("pages"))["total"] or 0


def current_streak(today: date | None = None) -> int:
    """Consecutive days with a reading log, ending today (or yesterday if
    nothing was logged today yet)."""
    today = today or date.today()
    logged = set(ReadingLog.objects.filter(pages__gt=0).values_list("date", flat=True))
    day = today if today in logged else today - timedelta(days=1)
    streak = 0
    while day in logged:
        streak += 1
        day -= timedelta(days=1)
    return streak


def overdue_loans(today: date | None = None):
    today = today or date.today()
    return Loan.objects.filter(returned_at__isnull=True, due_at__lt=today)


def summary(today: date | None = None) -> dict:
    today = today or date.today()
    return {
        "total_books": Book.objects.count(),
        "books_finished_this_month": books_finished_this_month(today),
        "total_pages_read": total_pages_read(),
        "current_streak_days": current_streak(today),
        "books_lent_out": Loan.objects.filter(returned_at__isnull=True).count(),
        "overdue_loans": overdue_loans(today).count(),
        "monthly": books_finished_by_month(today=today),
    }
