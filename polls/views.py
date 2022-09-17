from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Choice, Question
from django.contrib.auth.decorators import login_required


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
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def detail(self, request, pk):
        poll = get_object_or_404(Question, pk=pk)
        if not poll.can_vote():
            messages.info(request, 'Voting is not allowed now')
            return redirect('polls:index')
        return render(request, 'polls/detail.html', {'question': poll})



class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


@login_required(login_url='/accounts/login')
def vote(request, question_id):
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
        if question.can_vote():
            selected_choice.votes += 1
            selected_choice.save()
            # after voting it will redirct to result page
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
        else:
            # if question is expired it will redirect to the index page.
            messages.error(request, "User can't vote this question.")
            return HttpResponseRedirect(reverse('polls:index'))


class EyesOnlyView(LoginRequiredMixin, generic.ListView):
    # this is the default. Same default as in auth_required decorator
    login_url = '/accounts/login/'