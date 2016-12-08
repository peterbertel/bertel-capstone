from django.shortcuts import render
from django.http import HttpResponse

from .models import Team, Game

import nflgame

def week_view(request):
	teams = Team.objects.all()
	games = Game.objects.all() #instead, filter the games based on the week

	w = int(request.GET.get('w', 1))

	context = {'games': games, 'teams': teams, 'week': w}

	return render(request, 'nfl_scores/week_view.html', context)

def load_games(request):
	# do all this only after the teams have been updated in the DB
	# check if there are games for the given weeks
		#basically, see if there is any updated nfl game data you need to load into your db
	# use the nflgame module to load in the games you don't have
	# if it is a week that has not happened yet, populate the data with an external api
	
	# maybe need to load in the teams first
	n = 0

	w = int(request.GET.get('w', 1))
	games = nflgame.games(2016, week=w)

	if len(games) == 0:
		return HttpResponse('This week has not happened yet, get the data some other way')

	for game in games:
		home_team = Team.objects.filter(short_name=game.home)
		away_team = Team.objects.filter(short_name=game.away)

		g = Game(home_team=home_team, away_team=away_team, week=w, home_score=game.score_home, away_score=game.score_away, \
			home_points_q1=game.score_home_q1, home_points_q2=game.score_home_q2, home_points_q3=game.score_home_q3, \
			home_points_q4=game.score_home_q4, away_points_q1=game.score_away_q1, away_points_q2=game.score_away_q2, \
			away_points_q3=game.score_away_q3, away_points_q4=game.score_away_q4)

		g.save()
		n += 1

	return HttpResponse('Loaded %d games' % n)

def load_teams(request):

	# parses the teams so we can interpret them better
	for team in nflgame.teams:
		# This is done to avoid the duplication of the old St. Louis Rams
		#	and the new Los Angeles Rams in the nflgame database
		if team[0] == "STL":
			continue

		t = Team(short_name=team[0], long_name=team[2])
		t.save()
	return HttpResponse('Loaded the teams:')

def update_records(request):
	return HttpResponse("Updated the teams's records")