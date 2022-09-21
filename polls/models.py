""" These are module contains the Question and Choice models."""
import datetime
from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User


class Question(models.Model):
    """ Creating questions."""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    end_date = models.DateTimeField('date ended', null=True)

    def __str__(self):
        """ return string of question"""
        return self.question_text

    @admin.display(
        boolean=True,
        ordering='pub_date',
        description='Voting time',
    )
    
    def was_published_recently(self):
        """ return boolean whether it was published recently."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """ return boolean whether the question was published."""
        return timezone.localtime() >= self.pub_date

    def can_vote(self):
        """ return boolean whether vote is allowed."""
        if self.end_date:
            return self.pub_date <= timezone.localtime() <= self.end_date
        return self.is_published()


class Choice(models.Model):
    """ Creating choices """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self) -> int:
        """ get or set vote """
        return Vote.objects.filter(choice=self).count()

    def __str__(self):
        """ return string of choice """
        return self.choice_text


class Vote(models.Model):
    """ all vote model """

    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    
    @property
    def question(self) -> Question:
        return self.choice.question