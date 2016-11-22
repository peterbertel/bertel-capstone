from django.shortcuts import render
from django.http import HttpResponse

from .models import Team, Game

def week_view(request):
	teams = Team.objects.all()
	games = Game.objects.all()

	w = int(request.GET.get('w', 1))

	context = {'games': games, 'teams': teams, 'week': w}

	return render(request, 'nfl_scores/week_view.html', context)