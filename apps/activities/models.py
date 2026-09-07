import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class SchoolYear(models.Model):
    name = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Activity(models.Model):
    group_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    schedule = models.CharField(max_length=200)
    provider = models.CharField(max_length=200)
    age_group = models.CharField(max_length=100)
    space = models.CharField(max_length=200)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    minimum_participants = models.PositiveIntegerField()
    maximum_participants = models.PositiveIntegerField()
    registration_count = models.PositiveIntegerField(default=0)
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="activities",
    )
    is_archived = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def clean(self):
        super().clean()
        if (
            self.minimum_participants is not None
            and self.maximum_participants is not None
            and self.minimum_participants > self.maximum_participants
        ):
            raise ValidationError(
                {
                    "maximum_participants": (
                        "Maximum participants must be greater than or equal to minimum participants."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.only("group_code").get(pk=self.pk)
            self.group_code = original.group_code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.group_code})"