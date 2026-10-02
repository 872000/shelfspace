"""Server-rendered UI views for ShelfSpace."""
from datetime import date

from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from . import isbn_lookup, stats
from .forms import BookForm, ISBNLookupForm, LoanForm, ReadingLogForm
from .models import Book, Loan


def dashboard(request):
    return render(request, "library/dashboard.html", {
        "summary": stats.summary(),
        "overdue": stats.overdue_loans(),
        "recent_books": Book.objects.all().order_by("-date_added")[:8],
    })


def book_list(request):
    status_filter = request.GET.get("status", "")
    books = Book.objects.all()
    if status_filter in dict(Book.Status.choices):
        books = books.filter(status=status_filter)
    return render(request, "library/book_list.html",
                  {"books": books, "status_filter": status_filter})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    loan_form = LoanForm()
    log_form = ReadingLogForm()
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "lend":
            loan_form = LoanForm(request.POST)
            if loan_form.is_valid():
                loan = loan_form.save(commit=False)
                loan.book = book
                try:
                    loan.save()
                except ValidationError as exc:
                    loan_form.add_error(None, exc)
                else:
                    messages.success(request, f"Lent to {loan.friend_name}.")
                    return redirect("library:book_detail", pk=book.pk)
        elif action == "log":
            log_form = ReadingLogForm(request.POST)
            if log_form.is_valid():
                entry = log_form.save(commit=False)
                entry.book = book
                entry.save()
                messages.success(request, "Reading logged.")
                return redirect("library:book_detail", pk=book.pk)
        elif action == "finish":
            book.status = Book.Status.FINISHED
            book.date_finished = date.today()
            book.save(update_fields=["status", "date_finished"])
            messages.success(request, "Marked as finished.")
            return redirect("library:book_detail", pk=book.pk)
    return render(request, "library/book_detail.html",
                  {"book": book, "loan_form": loan_form, "log_form": log_form})


def book_add(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            messages.success(request, f"Added {book.title}.")
            return redirect("library:book_detail", pk=book.pk)
    else:
        form = BookForm()
    return render(request, "library/form.html", {"form": form, "title": "Add a book"})


def book_add_isbn(request):
    """Add a book via the offline ISBN stub (no network calls)."""
    result = None
    if request.method == "POST":
        form = ISBNLookupForm(request.POST)
        if form.is_valid():
            result = isbn_lookup.lookup_isbn(form.cleaned_data["isbn"])
            if result is None:
                messages.warning(request, "ISBN not in the offline catalog — add it manually.")
            else:
                book = Book.objects.create(
                    title=result["title"], author=result["author"],
                    isbn=result["isbn"], pages=result["pages"])
                messages.success(request, f"Added {book.title} from the offline catalog.")
                return redirect("library:book_detail", pk=book.pk)
    else:
        form = ISBNLookupForm()
    return render(request, "library/isbn_lookup.html",
                  {"form": form, "result": result,
                   "catalog_size": isbn_lookup.catalog_size()})


def loan_list(request):
    active = Loan.objects.filter(returned_at__isnull=True)
    returned = Loan.objects.exclude(returned_at__isnull=True)[:20]
    return render(request, "library/loan_list.html", {
        "overdue": stats.overdue_loans(),
        "active": active,
        "returned": returned,
    })


def loan_return(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if loan.returned_at is None:
        loan.returned_at = date.today()
        loan.save(update_fields=["returned_at"])
        messages.success(request, f"{loan.book.title} returned.")
    return redirect("library:loan_list")


def log_list(request):
    from .models import ReadingLog
    return render(request, "library/log_list.html",
                  {"logs": ReadingLog.objects.all()[:30]})
