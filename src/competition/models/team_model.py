from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug
from django.contrib.auth.models import User

from competition.models.competition_model import Competition
from competition.validators import validate_name, positive, greater_than_zero


class Team(models.Model):
    class Meta:
        app_label = 'competition'
        unique_together = (('competition', 'slug'),)

    competition = models.ForeignKey(Competition)
    members = models.ManyToMany(User)

    name = models.CharField(max_length=50, validators=[validate_name])
    slug = models.CharField(max_length=50, validators=[validate_slug])

    picture = models.ImageField()

    paid = models.BooleanField(default=False)
    time_paid = models.DateTimeField()

    created = models.DateTimeField(auto_add_now=True)
    eligible_to_win = models.BooleanField(default=True)

    @models.permalink
    def get_absolute_url(self):
        kwds = {'comp_slug': self.competition.slug, 'slug': self.slug}
        return ('team_detail', (), kwds)


@receiver(pre_save, sender=Team)
def team_pre_save(sender, instance, **kwargs):
    """Called before a Team is saved
    """
    instance.slug = slugify(instance.name)
