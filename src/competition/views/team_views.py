from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView

from competition.models.team_model import Team
from competition.views.mixins import (CompetitionViewMixin, LoggedInMixin,
                                      UserRegisteredMixin, ConfirmationMixin,
                                      CheckAllowedMixin)
from competition.forms.team_forms import TeamForm


class TeamListView(LoggedInMixin, CompetitionViewMixin, ListView):
    """Lists all teams, provided that the user is logged in"""
    context_object_name = 'teams'
    template_name = 'competition/team/team_list.html'
    paginate_by = 10

    def get_queryset(self):
        """Only list teams participating in self.get_competition()"""
        return Team.objects.filter(competition=self.get_competition())


class TeamDetailView(LoggedInMixin, CompetitionViewMixin, DetailView):
    """Show details about a particular team"""
    template_name = 'competition/team/team_detail.html'
    context_object_name = 'team'

    def get_queryset(self):
        """Only list teams participating in self.get_competition()"""
        return Team.objects.filter(competition=self.get_competition())


class TeamCreationView(UserRegisteredMixin,
                       CheckAllowedMixin,
                       CreateView):
    """Allow users to create new teams"""
    template_name = 'competition/team/team_create.html'
    form_class = TeamForm

    def get_team(self, request):
        """Returns any teams the user may already be on. We have
        access to get_competition since UserRegisteredMixin inherits
        from CompetitionViewMixin. Also, we have access to
        self.request.user since we inherit UserRegisteredMixin also
        inherits from FancyView"""
        user = request.user
        competition = self.get_competition()
        try:
            return user.team_set.get(competition=competition)
        except Team.DoesNotExist:
            return None

    def check_if_allowed(self, request):
        """Checks to see if the user is already on a team. If they
        are, send them a 404"""
        # If they're not on a team, they can create a team.
        return self.get_team(request) is None
        

    def get_error_message(self, request):
        """Called when the user isn't allowed to create a new team
        """
        msg = 'If you would like to create a new team, '
        msg += 'please leave "%s" first' % self.get_team(request).name
        return msg

    def form_valid(self, form):
        try:
            team = form.save()
            team.add_team_member(self.request.user)
            return super(TeamCreationView, self).form_valid(form)
        except IntegrityError:
            # If a (competition, team_slug) pair already exists,
            # return the invalid form
            return super(TeamCreationView, self).form_invalid(form)

    def get_form_kwargs(self):
        # Add competition as a keyword argument
        kwargs = super(TeamCreationView, self).get_form_kwargs()
        kwargs['instance'] = Team(competition=self.get_competition())
        return kwargs


class TeamLeaveView(UserRegisteredMixin,
                    ConfirmationMixin):
    template_name = 'competition/team/team_leave.html'

    def get_team(self):
        return get_object_or_404(Team, members=self.request.user,
                                 competition=self.get_competition())

    def get_question(self):
        team = self.get_team()
        return "Are you sure you want to leave %s?" % team.name

    def get_check_box_label(self):
        return "Yes I'm sure"

    def agreed(self):
        team = self.get_team()
        team.members.remove(self.request.user)

        msg = "Successfully left team %s" % team.name
        messages.success(self.request, msg)
        return redirect(self.get_competition())

    def disagreed(self):
        return redirect(self.get_team())
