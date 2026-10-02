from django.urls import path
from rest_framework.routers import DefaultRouter

from . import api

router = DefaultRouter()
router.register(r"books", api.BookViewSet, basename="book")
router.register(r"loans", api.LoanViewSet, basename="loan")
router.register(r"reading-logs", api.ReadingLogViewSet, basename="readinglog")

urlpatterns = [
    path("isbn/", api.isbn_lookup_view, name="isbn_lookup"),
    path("stats/", api.stats_view, name="stats"),
] + router.urls
