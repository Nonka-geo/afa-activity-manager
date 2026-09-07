import uuid

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_assign_editor_permission"),
    ]

    operations = [
        migrations.CreateModel(
            name="SchoolYear",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20, unique=True)),
                ("is_active", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Activity",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "group_code",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("schedule", models.CharField(max_length=200)),
                ("provider", models.CharField(max_length=200)),
                ("age_group", models.CharField(max_length=100)),
                ("space", models.CharField(max_length=200)),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=10,
                        validators=[django.core.validators.MinValueValidator(0)],
                    ),
                ),
                ("minimum_participants", models.PositiveIntegerField()),
                ("maximum_participants", models.PositiveIntegerField()),
                ("registration_count", models.PositiveIntegerField(default=0)),
                ("is_archived", models.BooleanField(default=False)),
                ("notes", models.TextField(blank=True)),
                (
                    "school_year",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="activities",
                        to="activities.schoolyear",
                    ),
                ),
            ],
        ),
    ]