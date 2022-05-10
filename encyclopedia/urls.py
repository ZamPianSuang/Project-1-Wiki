from django.urls import path

from . import views

app_name = "encyclopedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("newpage", views.newpage, name="new"),        # Tricking by putting before entry path
    path("rand", views.rand, name="rand"),         # Tricking by putting before entry path
    path("search", views.search, name="search"),
    path("<str:title>/edit", views.edit, name="edit"),
    path("<str:title>", views.entries, name="entries")
]
