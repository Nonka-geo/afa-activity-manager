from django.db import migrations


ACTIVITY_PERMISSIONS = (
    ("view_activity", "Can view activity"),
    ("add_activity", "Can add activity"),
    ("change_activity", "Can change activity"),
)


def assign_activity_permissions(apps, schema_editor):
    content_type_model = apps.get_model("contenttypes", "ContentType")
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")
    activity_content_type, _ = content_type_model.objects.get_or_create(
        app_label="activities",
        model="activity",
    )
    permissions = []
    for codename, name in ACTIVITY_PERMISSIONS:
        permission, _ = permission_model.objects.get_or_create(
            content_type=activity_content_type,
            codename=codename,
            defaults={"name": name},
        )
        permissions.append(permission)

    viewer_group = group_model.objects.get(name="Viewer")
    editor_group = group_model.objects.get(name="Admin/Editor")
    viewer_group.permissions.add(permissions[0])
    viewer_group.permissions.remove(*permissions[1:])
    editor_group.permissions.add(*permissions)


def remove_activity_permissions(apps, schema_editor):
    content_type_model = apps.get_model("contenttypes", "ContentType")
    permission_model = apps.get_model("auth", "Permission")
    activity_content_type = content_type_model.objects.filter(
        app_label="activities",
        model="activity",
    ).first()
    if activity_content_type is not None:
        permission_model.objects.filter(content_type=activity_content_type).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("activities", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(assign_activity_permissions, remove_activity_permissions),
    ]