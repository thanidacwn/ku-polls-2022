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
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView, LoginRequiredMixin):
    """Class based view for viewing a poll."""
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        error = None
        user = request.user
        try:
            question = get_object_or_404(Question, pk=kwargs['pk'])
        except Http404:
            error = '404'
        # if question is expired show a error and redirect to index
        if error == '404' or not question.can_vote():
            messages.error(
                request, "This question is not available for voting.")
            return HttpResponseRedirect(reverse('polls:index'))
        try:
            if not user.is_authenticated:
                raise Vote.DoesNotExist
            user_vote = question.vote_set.get(user=user).choice
        except Vote.DoesNotExist:

            # if user didnt select a choice or invalid cho[ice
            # it will render as didnt select a choice
            return super().get(request, *args, **kwargs)
        else:
            # go to polls detail application
            return render(request, 'polls/detail.html', {
                'question': question,
                'user_vote': user_vote,
            })


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


@login_required(login_url='/accounts/login')
def vote(request: HttpRequest, question_id):
    """Vote for a choice on a question (poll)."""

    user = request.user
    if not user.is_authenticated:
       return redirect('login')
    question = get_object_or_404(Question, pk=question_id)

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        # to vote it and save the result
        try:
            vote_ob = Vote.objects.get(user=user)
            vote_ob.choice = selected_choice
            vote_ob.save()
        except Vote.DoesNotExist:
            Vote.objects.create(user=user, choice=selected_choice, 
            question=selected_choice.question).save()

        # after voting it will redirct to result page
        else:
            # if question is expired it will redirect to the index page.
            messages.error(request, "User can't vote this question.")
            return HttpResponseRedirect(reverse('polls:index'))

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


class EyesOnlyView(LoginRequiredMixin, generic.ListView):
    # this is the default. Same default as in auth_required decorator
    login_url = '/accounts/login/'


def signup(request):
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