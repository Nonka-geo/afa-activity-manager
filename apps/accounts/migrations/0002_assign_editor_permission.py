from django.db import migrations


PERMISSION_CODENAME = "access_editor_endpoint"
PERMISSION_NAME = "Can access editor-protected endpoints"


def assign_editor_permission(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")
    content_type_model = apps.get_model("contenttypes", "ContentType")
    user_content_type, _ = content_type_model.objects.get_or_create(
        app_label="auth",
        model="user",
    )
    permission, _ = permission_model.objects.get_or_create(
        content_type=user_content_type,
        codename=PERMISSION_CODENAME,
        defaults={"name": PERMISSION_NAME},
    )
    group_model.objects.get(name="Admin/Editor").permissions.add(permission)
    group_model.objects.get(name="Viewer").permissions.remove(permission)


def remove_editor_permission(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")
    content_type_model = apps.get_model("contenttypes", "ContentType")
    user_content_type = content_type_model.objects.get(app_label="auth", model="user")
    permission = permission_model.objects.filter(
        content_type=user_content_type,
        codename=PERMISSION_CODENAME,
    ).first()
    if permission is not None:
        permission.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_create_roles"),
    ]

    operations = [
        migrations.RunPython(assign_editor_permission, remove_editor_permission),
    ]
