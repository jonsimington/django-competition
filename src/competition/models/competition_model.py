from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete, post_syncdb
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from competition.models.avatar_model import Avatar
from competition.validators import (validate_name, non_negative,
                                    greater_than_zero)


class Competition(models.Model):
    class Meta:
        app_label = 'competition'
        ordering = ['-is_running', '-is_open', '-start_time']
        permissions = (
            ("moderate_teams", "Can moderate team names and avatars"),
            ("view_registrations", "Can view competitor registrations"),
            ("mark_paid", "Can mark a registration as paid"),
        )

    # Typical info
    name = models.CharField(max_length=50, unique=True,
                            help_text="Name of the competition",
                            validators=[validate_name])
    slug = models.CharField(max_length=50,
                            primary_key=True, blank=True, editable=False,
                            validators=[validate_slug])
    description = models.TextField(help_text="Describe the competition")
    avatar = models.OneToOneField(Avatar, blank=True, null=True)

    # These are the scheduled start and end times for a competition
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Whether or not the competition is running
    is_open = models.BooleanField(default=False)
    is_running = models.BooleanField(default=False)

    # Questions to ask registering competitors
    questions = models.ManyToManyField("competition.RegistrationQuestion",
                                       blank=True, null=True)

    cost_per_person = models.FloatField(validators=[non_negative])

    # Team details
    min_num_team_members = models.IntegerField(verbose_name="Minimum number " +
                                               "of players per team",
                                               validators=[greater_than_zero])
    max_num_team_members = models.IntegerField(verbose_name="Maximum number " +
                                               "of players per team",
                                               validators=[greater_than_zero])

    @models.permalink
    def get_absolute_url(self):
        return ('competition_detail', (), {'comp_slug': self.slug})

    def clean(self):
        if self.start_time > self.end_time:
            raise ValidationError("Start time is after end time.")

        if self.min_num_team_members > self.max_num_team_members:
            raise ValidationError("Max number of team members must be " +
                                  " greater than or equal to the min number" +
                                  " of team membeers")

    def __str__(self):
        return self.name

    def is_user_registered(self, user):
        """Return true if the given user has an **active**
        registration for this competition, else return false"""
        return self.registration_set.filter(user=user, active=True).exists()

    @staticmethod
    def get_organizer_permissions():
        """Returns the permission codes for a competition organizer"""
        return [p[0] for p in Competition._meta.permissions]


@receiver(pre_save, sender=Competition)
def competition_pre_save(sender, instance, **kwargs):
    """Called before a Competition is saved

    Updates the competition's slug
    """
    instance.slug = slugify(instance.name)


@receiver(pre_delete, sender=Competition)
def competition_pre_delete(sender, instance, **kwargs):
    """Called before a Competition is deleted
    """
    pass


@receiver(post_syncdb, sender=Competition)
def my_callback(sender, **kwargs):
    Group.objects.create(name="Competition Staff")
