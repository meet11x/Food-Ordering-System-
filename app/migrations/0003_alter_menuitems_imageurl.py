# Generated by Django 5.0.3 on 2024-03-31 04:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_cartitem_delete_admins_remove_delivery_courierid_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="menuitems",
            name="ImageURL",
            field=models.ImageField(blank=True, null=True, upload_to="MenuImages/"),
        ),
    ]