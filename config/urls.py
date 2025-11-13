from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/transactions/upload", views.UploadCSVView.as_view()),
    path("api/transactions",        views.TransactionsView.as_view()),
    path("api/insights",            views.InsightsView.as_view()),
    path("api/nudges",              views.NudgesView.as_view()),
    path("api/nudges/suggest",      views.SuggestNudgesView.as_view()),
    # path("api/dev/reset",           views.DevResetView.as_view()),  # optional
]