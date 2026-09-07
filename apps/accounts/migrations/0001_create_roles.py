from django.db import migrations


ROLE_NAMES = ("Admin/Editor", "Viewer")
EDITOR_PERMISSION_CODENAME = "access_editor_endpoint"
EDITOR_PERMISSION_NAME = "Can access editor-protected endpoints"


def create_roles(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")
    content_type_model = apps.get_model("contenttypes", "ContentType")
    for role_name in ROLE_NAMES:
        group_model.objects.get_or_create(name=role_name)

    user_content_type, _ = content_type_model.objects.get_or_create(
        app_label="auth",
        model="user",
    )
    editor_permission, _ = permission_model.objects.get_or_create(
        content_type=user_content_type,
        codename=EDITOR_PERMISSION_CODENAME,
        defaults={"name": EDITOR_PERMISSION_NAME},
    )
    editor_group = group_model.objects.get(name="Admin/Editor")
    editor_group.permissions.add(editor_permission)
    group_model.objects.get(name="Viewer").permissions.remove(editor_permission)


def remove_roles(apps, schema_editor):
    group_model = apps.get_model("auth", "Group")
    permission_model = apps.get_model("auth", "Permission")
    content_type_model = apps.get_model("contenttypes", "ContentType")
    user_content_type = content_type_model.objects.get(app_label="auth", model="user")
    permission_model.objects.filter(
        content_type=user_content_type,
        codename=EDITOR_PERMISSION_CODENAME,
    ).delete()
    group_model.objects.filter(name__in=ROLE_NAMES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_roles, remove_roles),
    ]
