from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging
import uuid

logger = logging.getLogger(__name__)

class Competition(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'instructor'},
        related_name='competitions_created'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    question_time_limit = models.PositiveIntegerField(
        help_text="Time limit per question in seconds"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
        if self.question_time_limit <= 0:
            raise ValidationError("Question time limit must be positive.")

    def save(self, *args, **kwargs):
        self.full_clean()
        now = timezone.now()
        logger.info(f"Saving competition '{self.title}': now={now}, start_time={self.start_time}, end_time={self.end_time}")
        if self.end_time < now:
            self.is_active = False
            logger.info(f"Competition '{self.title}' set to inactive because end_time ({self.end_time}) is before now ({now})")
        else:
            self.is_active = True
            logger.info(f"Competition '{self.title}' set to active because end_time ({self.end_time}) is after now ({now})")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        now = timezone.now()
        is_ongoing = self.start_time <= now <= self.end_time and self.is_active
        logger.info(f"Checking is_ongoing for '{self.title}': start_time={self.start_time}, end_time={self.end_time}, now={now}, is_active={self.is_active}, result={is_ongoing}")
        return is_ongoing

class Question(models.Model):
    QUESTION_TYPES = [
        ('MCQ', 'Multiple Choice'),
        ('TEXT', 'Text Answer'),
    ]
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='MCQ')
    choices = models.TextField(
        blank=True,
        help_text="For MCQ, enter choices as comma-separated values (e.g., 'A,B,C,D')"
    )
    correct_answer = models.CharField(max_length=255)
    points = models.PositiveIntegerField(default=10)
    coins = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"{self.text} ({self.competition.title})"

class Participant(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'},
        related_name='participations'
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    total_xp = models.PositiveIntegerField(default=0)
    total_coins = models.PositiveIntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'competition')

    def __str__(self):
        return f"{self.user.username} in {self.competition.title}"

class Answer(models.Model):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    answer_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('participant', 'question')

    def save(self, *args, **kwargs):
        if not self.pk:
            answer_text = self.answer_text.strip() if self.answer_text else ""
            correct_answer = self.question.correct_answer.strip() if self.question.correct_answer else ""
            if self.question.question_type == 'MCQ':
                self.is_correct = answer_text.lower() == correct_answer.lower()
                logger.info(f"MCQ Answer check: answer_text='{answer_text}', correct_answer='{correct_answer}', is_correct={self.is_correct}")
            else:
                self.is_correct = answer_text.lower() == correct_answer.lower()
                logger.info(f"TEXT Answer check: answer_text='{answer_text}', correct_answer='{correct_answer}', is_correct={self.is_correct}")
            if self.is_correct:
                points = self.question.points or 10
                coins = self.question.coins or 10
                logger.info(f"Correct answer for question '{self.question.text}': adding {points} XP and {coins} Coins to participant {self.participant.user.username}")
                self.participant.total_xp += points
                self.participant.total_coins += coins
                self.participant.save()
                try:
                    profile = self.participant.user.profile
                    profile.xp = (profile.xp or 0) + points
                    profile.coins = (profile.coins or 0) + coins
                    profile.save()
                    logger.info(f"Updated user profile: xp={profile.xp}, coins={profile.coins}")
                except AttributeError as e:
                    logger.error(f"Failed to update user profile: {str(e)}")
                try:
                    courses_profile = self.participant.user.courses_profile
                    courses_profile.add_coins(coins)
                    logger.info(f"Updated courses profile: added {coins} coins")
                except AttributeError as e:
                    logger.error(f"Failed to update courses profile: {str(e)}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer by {self.participant.user.username} to {self.question.text}"

class Certificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='competition_certificates'
    )
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    certificate_number = models.CharField(max_length=36, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'competition')

    def __str__(self):
        return f"Certificate for {self.user.username} in {self.competition.title}"