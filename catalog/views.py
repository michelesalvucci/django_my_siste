# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

'''Utilities'''
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime

''' DECORATORS FUNZIONI login, permission'''
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

''' SUPERCLASSI login, permission'''
""" Per Classi """
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

""" View """
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

""" Creating e editing delle view """
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

""" Models """
from .models import Book, Author, BookInstance
from .forms import RenewBookForm, RenewBookModelForm


def index(request):
    """
    View function for home page of site.
    """
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Challenge
    my_books = Book.objects.filter(author__last_name__icontains='salvucci').count()

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable
    return render(
        request,
        'index.html',
        context={'num_books': num_books,
                 'num_instances': num_instances,
                 'num_instances_available': num_instances_available,
                 'num_authors': num_authors,
                 'my_books': my_books,
                 'num_visits': num_visits,
                 },
    )


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('borrowed'))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        # form = RenewBookForm(initial={'renewal_date': proposed_renewal_date, })
        form = RenewBookModelForm(initial={'renewal_date': proposed_renewal_date, })

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': book_inst})

""" AUTHOR EDIT """
class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'05/01/2018',}
    template_name_suffix = '_editable_form'

    # Permission
    permission_required = 'catalog.can_mark_returned'


class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']
    template_name_suffix = '_editable_form'

    # Permission
    permission_required = 'catalog.can_mark_returned'


class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    # Reverse lazy e' un reverse che rimanda a un url class based non return HttpResponseRedirect(reverse('authors'))
    success_url = reverse_lazy('authors')
    template_name_suffix = "_confirm_delete"

    # Permission
    permission_required = 'catalog.can_mark_returned'


""" BOOK EDIT """
class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = '__all__'
    template_name_suffix = '_editable_form'
    # Permission
    permission_required = 'catalog.can_mark_returned'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = '__all__'
    template_name_suffix = '_editable_form'
    # Permission
    permission_required = 'catalog.can_mark_returned'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    # Reverse lazy e' un reverse che rimanda a un url class based non return HttpResponseRedirect(reverse('authors'))
    success_url = reverse_lazy('books')
    template_name_suffix = "_confirm_delete"
    # Permission
    permission_required = 'catalog.can_mark_returned'


class BookListView(ListView):
    model = Book
    # context_object_name = 'book_list'  # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='il')
    # queryset = Book.objects.all()
    template_name = 'book_list.html'

    paginate_by = 1

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['book_list'] = Book.objects.all()
        return context


class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    # login_url = '/login/' # per overridare settings.LOGIN
    # redirect_field_name = 'redirect_to' # per overrideare il next.path


class AuthorListView(PermissionRequiredMixin, ListView):
    model = Book
    template_name = 'author_list.html'

    paginate_by = 10

    permission_required = 'catalog.can_mark_returned'

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        context['author_list'] = Author.objects.all()
        return context


class AuthorDetailView(DetailView):
    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, ListView):
    """
    Generic class-based view listing books on loan to current user.
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class LoanedBooksListView(PermissionRequiredMixin, ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_all_borrowed.html'

    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.all().order_by('due_back')

