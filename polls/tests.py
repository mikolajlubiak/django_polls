import datetime
from django.http import response

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Question


def create_question(question_text, pub_date):
    return Question.objects.create(question_text=question_text, pub_date=pub_date)


class QuestionModelTest(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)


class QuestionViewIndexTest(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_questions"], [])

    def test_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23)
        question = create_question("Recent question", time)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_questions"],
            [question],
        )

    def test_past_question(self):
        time = timezone.now() - datetime.timedelta(days=10)
        create_question("Past question", time)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_questions"],
            [],
        )

    def test_future_question(self):
        time = timezone.now() + datetime.timedelta(days=1)
        create_question("Future question", time)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available.")
        self.assertQuerySetEqual(response.context["latest_questions"], [])

    def test_future_and_recent_question(self):
        time_future = timezone.now() + datetime.timedelta(days=1)
        time_recent = timezone.now() - datetime.timedelta(hours=23)
        create_question("Future question", time_future)
        recent_question = create_question("Recent question", time_recent)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_questions"], [recent_question]
        )

    def test_future_and_past_question(self):
        time_future = timezone.now() + datetime.timedelta(days=1)
        time_past = timezone.now() - datetime.timedelta(days=10)
        create_question("Future question", time_future)
        create_question("Past question", time_past)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(response.context["latest_questions"], [])

    def test_two_recent_questions(self):
        time1 = timezone.now() - datetime.timedelta(hours=23)
        time2 = timezone.now() - datetime.timedelta(seconds=1)
        question1 = create_question("Recent question 1", time1)
        question2 = create_question("Recent question 2", time2)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerySetEqual(
            response.context["latest_questions"],
            [question2, question1],
        )


class QuestionViewDetailTest(TestCase):
    def test_future_question(self):
        time = timezone.now() + datetime.timedelta(days=1)
        question = create_question("Future question", time)
        url = reverse("polls:detail", args=(question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        time = timezone.now() - datetime.timedelta(days=10)
        question = create_question("Past question", time)
        url = reverse("polls:detail", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)

    def test_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23)
        question = create_question("Recent question", time)
        url = reverse("polls:detail", args=(question.id,))
        response = self.client.get(url)
        self.assertContains(response, question.question_text)
