from django.db.models import F
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Question, Choice


def index(request):
    latest_questions = Question.objects.order_by("-pub_date")[:5]
    context = {"latest_questions": latest_questions}
    return render(request, "polls/index.html", context)


def detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    context = {"question": question}
    return render(request, "polls/detail.html", context)


def results(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    choices = question.choice_set.order_by("-votes")
    context = {"question": question, "choices": choices}
    return render(request, "polls/results.html", context)


def vote(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    try:
        choice = question.choice_set.get(id=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        choice.votes = F("votes") + 1
        choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
