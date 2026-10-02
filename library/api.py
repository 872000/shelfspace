"""Django REST Framework API for ShelfSpace."""
from datetime import date

from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from . import isbn_lookup, stats
from .models import Book, Loan, ReadingLog
from .serializers import BookSerializer, LoanSerializer, ReadingLogSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class LoanViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.select_related("book").all()
    serializer_class = LoanSerializer

    def perform_create(self, serializer):
        try:
            serializer.save()
        except ValidationError as exc:
            from rest_framework.exceptions import ValidationError as DRFValidationError
            raise DRFValidationError({"non_field_errors": exc.messages})

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        loans = stats.overdue_loans(date.today())
        return Response(LoanSerializer(loans, many=True).data)

    @action(detail=True, methods=["post"])
    def mark_returned(self, request, pk=None):
        loan = self.get_object()
        if loan.returned_at is not None:
            return Response({"detail": "Loan already returned."},
                            status=status.HTTP_400_BAD_REQUEST)
        loan.returned_at = date.today()
        loan.save(update_fields=["returned_at"])
        return Response(LoanSerializer(loan).data)


class ReadingLogViewSet(viewsets.ModelViewSet):
    queryset = ReadingLog.objects.all()
    serializer_class = ReadingLogSerializer


@api_view(["GET"])
def isbn_lookup_view(request):
    """Offline ISBN lookup against the bundled catalog (no network)."""
    isbn = request.query_params.get("isbn", "")
    entry = isbn_lookup.lookup_isbn(isbn)
    if entry is None:
        return Response({"isbn": isbn_lookup.normalize_isbn(isbn), "found": False},
                        status=status.HTTP_404_NOT_FOUND)
    return Response({**entry, "found": True})


@api_view(["GET"])
def stats_view(request):
    return Response(stats.summary())
