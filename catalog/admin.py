# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Author, Genre, Book, BookInstance

# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)


# Creo una classe inline di BookInstance visualizzabile nel contesto di book tramite
# l'attributo inlines
class BookInline(admin.TabularInline):
    model = Book
    extra = 0


class AuthorAdmin(admin.ModelAdmin):
    # Override della variabile list_display (le variabili listate sono ottenute dal model
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    # Disposizione dei field layout (verticale, quelli tra parentesi sono orizzontali)
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookInline]


admin.site.register(Author, AuthorAdmin)


# @register e equivalente di admin.site.register()
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'status', 'borrower', 'due_back', 'imprint')
    # Override dei filtri da visualizzare
    list_filter = ('status', 'due_back')
    # Fieldsets per creare delle sezioni/separatori con intestazioni
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': [('status', 'due_back', 'borrower')]
        }),
    )


# Creo una classe inline di BookInstance visualizzabile nel contesto di book tramite
# l'attributo inlines
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Display_genre e' la funzione creata nel model del book per mostrare parzialmente i generi
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]
