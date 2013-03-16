import factory
import random
from datetime import timedelta
from datetime import datetime

from django.contrib.auth.models import User
from competition.models import (Competition, Game, Avatar, Team,
                                Organizer, OrganizerRole,
                                Registration, Invitation)
from competition.models import RegistrationQuestion as Question
from competition.models import RegistrationQuestionChoice as Choice
from competition.models import RegistrationQuestionResponse as Response


def now(_=None):
    """Returns the current time. Takes a single optional argument,
    which gets thrown away. The argument is to make factory_boy happy.
    """
    return datetime.now()


def later(_=None):
    """Returns the current time + 12 hours. Takes a single optional
    argument, which gets thrown away. The argument is to make
    factory_boy happy.
    """
    return datetime.now() + timedelta(hours=12)


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'user' + n)
    password = "123"

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user


class CompetitionFactory(factory.Factory):
    FACTORY_FOR = Competition

    name = factory.Sequence(lambda n: "MegaMinerAI: %s" % n)
    start_time = factory.LazyAttribute(now)
    end_time = factory.LazyAttribute(later)
    cost = 8.00
    min_num_team_members = 1
    max_num_team_members = 3
    description = "This is the best MegaMinerAI ever yay!"


class GameFactory(factory.Factory):
    FACTORY_FOR = Game

    competition = factory.SubFactory(CompetitionFactory)
    start_time = factory.LazyAttribute(now)
    end_time = factory.LazyAttribute(now)


class AvatarFactory(factory.Factory):
    FACTORY_FOR = Avatar


class TeamFactory(factory.Factory):
    FACTORY_FOR = Team

    competition = factory.SubFactory(CompetitionFactory)
    name = factory.Sequence(lambda n: "Team #%s" % n)

    @classmethod
    def _prepare(cls, create, **kwargs):
        """Register some users and add them as members of the new team"""
        num_choices = int(kwargs.pop('num_members', 3))
        team = super(TeamFactory, cls)._prepare(create, **kwargs)
        if team.members.count() == 0:
            for _i in range(num_choices):
                u = UserFactory.create()
                RegistrationFactory.create(user=u, competition=team.competition)
                team.add_team_member(u)
        return team


class OrganizerRoleFactory(factory.Factory):
    FACTORY_FOR = OrganizerRole

    name = factory.Sequence(lambda n: "Role #%s" % n)
    description = "Role description."


class OrganizerFactory(factory.Factory):
    FACTORY_FOR = Organizer

    user = factory.SubFactory(UserFactory)
    competition = factory.SubFactory(CompetitionFactory)

    @classmethod
    def _prepare(cls, create, **kwargs):
        """Add a role to the Organizer"""
        num_roles = int(kwargs.pop('num_roles', 1))
        organizer = super(OrganizerFactory, cls)._prepare(create, **kwargs)
        if num_roles > 0:
            for _i in range(num_roles):
                organizer.role.add(OrganizerRoleFactory.create())
        return organizer


class RegistrationFactory(factory.Factory):
    FACTORY_FOR = Registration

    user = factory.SubFactory(UserFactory)
    competition = factory.SubFactory(CompetitionFactory)


class RegistrationQuestionFactory(factory.Factory):
    FACTORY_FOR = Question

    question = factory.Sequence(lambda n: "Question #%s" % n)
    question_type = factory.LazyAttribute(
        lambda _: random.choice(Question.QUESTION_TYPES)[0]
    )

    @classmethod
    def _prepare(cls, create, **kwargs):
        num_choices = int(kwargs.pop('num_choices', 4))
        q = super(RegistrationQuestionFactory, cls)._prepare(create, **kwargs)
        if q.question_type in ('SC', 'MC'):
            for _i in range(num_choices):
                RegistrationQuestionChoiceFactory.create(question=q)
        return q


class RegistrationQuestionChoiceFactory(factory.Factory):
    FACTORY_FOR = Choice

    question = factory.SubFactory(RegistrationQuestionFactory)
    choice = factory.Sequence(lambda n: "Choice #%s" % n)


class RegistrationQuestionResponseFactory(factory.Factory):
    FACTORY_FOR = Response

    question = factory.SubFactory(RegistrationQuestionFactory)
    registration = factory.SubFactory(RegistrationFactory)


class InvitationFactory(factory.Factory):
    FACTORY_FOR = Invitation

    team = factory.SubFactory(TeamFactory)
    sender = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(UserFactory)
    message = factory.Sequence(lambda n: "Message #%s" % n)
