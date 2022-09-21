import datetime
from django.db import models
from django.utils import timezone


class Question(models.Model):
    """ Creating questions."""
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        """ return string of question"""
        return self.question_text
    
    def was_published_recently(self):
        """ return boolean whether it was published recently."""
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

class Choice(models.Model):
    """ Creating choices """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        """ return string of choice """
        return self.choice_text