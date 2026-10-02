from django.urls import path

from . import views

app_name = "library"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("books/", views.book_list, name="book_list"),
    path("books/add/", views.book_add, name="book_add"),
    path("books/add-isbn/", views.book_add_isbn, name="book_add_isbn"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("loans/", views.loan_list, name="loan_list"),
    path("loans/<int:pk>/return/", views.loan_return, name="loan_return"),
    path("log/", views.log_list, name="log_list"),
]
