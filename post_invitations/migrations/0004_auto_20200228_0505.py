# Generated by Django 2.2.5 on 2020-02-28 05:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('post_invitations', '0003_myinvitation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitationpost',
            name='invitation_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='invitation_id', to='post_invitations.MyInvitation'),
        ),
    ]
