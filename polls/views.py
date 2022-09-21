"""These are module contains the views of each page of the application."""

from django.http import HttpResponseRedirect, HttpRequest, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Choice, Question
from django.contrib.auth.decorators import login_required
from .models import Choice, Question, Vote


class IndexView(generic.ListView):
    """ Index page of application """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView, LoginRequiredMixin):
    """ Detail view showing the question detail."""
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """ Excludes any questions that aren't published yet """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, pk):
        """ return different pages in accordance to can_vote and is_published """
        if request.user.is_anonymous:
            return redirect(to='http://127.0.0.1:8000/accounts/login')
        user = request.user
        try:
            question = Question.objects.get(pk=pk)
        except (KeyError, Question.DoesNotExist):
            messages.error(request, 'Access to question denied.')
            return HttpResponseRedirect(reverse('polls:index'))
        if question.can_vote():
            try:
                vote_info = Vote.objects.get(user=user, choice__in=question.choice_set.all())
                check = vote_info.choice.choice_text
            except Vote.DoesNotExist:
                check = ''
            return render(request, 'polls/detail.html', {'question': question,
                                                         'check': check})
        elif question.is_published():
            messages.error(request, 'Voting period is closed for this question.')
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        messages.error(request, 'Access to question denied.')
        return HttpResponseRedirect(reverse('polls:index'))


class ResultsView(generic.DetailView):
    """ Result view showing the vote result """
    model = Question
    template_name = 'polls/results.html'

    def get(self, request, pk):
        """ Process the voting """
        try:
            question = Question.objects.get(pk=pk)
        except (KeyError, Question.DoesNotExist):
            messages.error(request, 'Access to question denied.')
            return HttpResponseRedirect(reverse('polls:index'))
        if question.is_published():
            return render(request, 'polls/results.html', {'question': question})
        messages.error(request, 'Access to question denied.')
        return HttpResponseRedirect(reverse('polls:index'))


class EyesOnlyView(LoginRequiredMixin, generic.ListView):
    # this is the default. Same default as in auth_required decorator
    login_url = '/accounts/login/'


@login_required
def vote(request, question_id):
    """Add vote to choice to current question."""
    question = get_object_or_404(Question, pk=question_id)
    user = request.user
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay question polls page
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        #check if user has been voted
        try:
            vote_info = Vote.objects.get(user=user, choice__in=question.choice_set.all())
            vote_info.choice = selected_choice
            vote_info.save()
        except Vote.DoesNotExist:
            Vote.objects.create(choice=selected_choice, user=user).save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def signup(request):
    """ create a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_passwd = form.cleaned_data.get('password')
            user = authenticate(username=username,password=raw_passwd)
            login(request, user)
            return redirect('polls')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})