from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import Http404

from ..models import Game
from .mixins import CompetitionViewMixin, RequireRunningMixin


class GameView(CompetitionViewMixin, RequireRunningMixin):

    def get_team(self):
        if self.request.user.is_anonymous():
            raise Http404("Anonymous user cannot view games")
        return get_object_or_404(self.request.user.team_set,
                                 competition=self.get_competition())

    def parse_data(self, games):
        fields = set()
        for game in games:
            try:
                fields.add(*game.data['display'].keys())
            except (KeyError, TypeError, AttributeError):
                pass
        return fields


class GameListView(GameView, ListView):
    paginate_by = 25
    context_object_name = 'games'
    template_name = 'competition/game/game_list.html'

    def get_queryset(self):
        self.team = self.get_team()
        q = Game.objects.prefetch_related('team1', 'team2', 'competition')
        q = q.filter(Q(team1=self.team)|Q(team2=self.team))
        return q.order_by('start_time')

    def get_context_data(self, **kwargs):
        context = super(GameListView, self).get_context_data(**kwargs)
        context['data_fields'] = self.parse_data(context['page_obj'])
        context['team'] = self.team
        return context


class GameDetailView(GameView, DetailView):
    template_name = 'competition/game/game_detail.html'

    def get_queryset(self):
        self.team = self.get_team()
        return Game.objects.filter(Q(team1=self.team)|Q(team2=self.team))

    def get_context_data(self, **kwargs):
        context = super(GameDetailView, self).get_context_data(**kwargs)
        context['data_fields'] = self.parse_data([self.object])
        context['team'] = self.team
        return context
