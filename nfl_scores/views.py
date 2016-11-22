from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

from .models import Team, Game

def week_view(request, week):
	teams = Team.objects.all()
	games = Game.objects.all()
	# team_output = ', '.join([str(team.name) for team in teams])
	# games = ', '.join([str(game) for game in games])

	context = {'games': games, 'teams': teams, 'week': week}

	return render(request, 'nfl_scores/week_view.html', context)

	# return HttpResponse("The current teams are: " + team_output + "\n" + games)