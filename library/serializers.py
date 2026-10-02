from rest_framework import serializers

from .models import Book, Loan, ReadingLog


class BookSerializer(serializers.ModelSerializer):
    is_available = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = "__all__"


class LoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)

    class Meta:
        model = Loan
        fields = "__all__"


class ReadingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingLog
        fields = "__all__"
