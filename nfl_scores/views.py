from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

# per-view caching found from
#	 https://docs.djangoproject.com/en/1.10/topics/cache/
from django.views.decorators.cache import cache_page

from .models import Team, Game

import nflgame
import httplib
import json

@cache_page(60 * 5)
def week_view(request, week_id):
	t = str(request.GET.get('t', 'NONE'))
	w = int(week_id)
	future_games = []

	if t != 'NONE':
		team = Team.objects.all().filter(long_name=t)[0]
		game = Game.objects.filter(week=w).filter(home_team=team)
		if len(game) == 0:
			game = Game.objects.filter(week=w).filter(away_team=team)
			if len(game) == 0:
				future_games = get_future_games(w, team.long_name)
				if len(future_games) == 0:
					return HttpResponse("This team is on bye this week")
		games = game
	else:
		games = Game.objects.filter(week=w)
		if len(games) == 0:
			future_games = get_future_games(w)

	context = {'games': games, 'week': w, 'future_games': future_games}

	return render(request, 'nfl_scores/week_view.html', context)

def get_future_games(week, team=''):
	conn = httplib.HTTPSConnection("api.sportradar.us")
	conn.request("GET", "/nfl-ot1/games/2016/reg/schedule.json?api_key=mk5mjt48drputswsxqct2uac")
	res = conn.getresponse()
	data = res.read()
	data = data.decode("utf-8")
	data = json.loads(data)
	future_games = data['weeks'][week-1]['games']
	if len(team) != 0:
		for game in future_games:
			if (team in game['home']['name']) or (team in game['away']['name']):
				future_game = []
				future_game.append(game)
				return future_game
		# return an empty array if the team does not play in
		#   the specified future week
		return []
	else:
		return future_games

# This method gets NFL game data for a particular week from the nflgame module and loads
# this data into the SQL database
def load_games(request):
	n = 0
	w = int(request.GET.get('w', 1))
	games = nflgame.games(2016, week=w)
	if len(games) == 0:
		return HttpResponse('This week has not happened yet, get the data some other way')

	for game in games:

		home_name = str(game.home)
		away_name = str(game.away)

		# Small hack in case the Jacksonville Jaguars games are inputted
		# with 'JAX' and not 'JAC'
		if str(game.home) == 'JAX':
			home_name = 'JAC'
		elif str(game.away) == 'JAX':
			away_name = 'JAC'

		home_team = Team.objects.filter(short_name=home_name)[0]
		away_team = Team.objects.filter(short_name=away_name)[0]

		# If the game is already in the database, don't add it again
		if len(Game.objects.filter(home_team=home_team, away_team=away_team, week=w)) > 0:
			continue

		g = Game(home_team=home_team, away_team=away_team, week=w, home_score=game.score_home, away_score=game.score_away, \
			home_points_q1=game.score_home_q1, home_points_q2=game.score_home_q2, home_points_q3=game.score_home_q3, \
			home_points_q4=game.score_home_q4, away_points_q1=game.score_away_q1, away_points_q2=game.score_away_q2, \
			away_points_q3=game.score_away_q3, away_points_q4=game.score_away_q4)

		g.save()
		n += 1

	return HttpResponse('Loaded %d games' % n)

def load_teams(request):
	n = 0
	# parses the teams so we can interpret them better
	for team in nflgame.teams:
		# This is done to avoid the duplication of the old St. Louis Rams
		#	and the new Los Angeles Rams in the nflgame database
		if str(team[0]) == "STL":
			continue

		t = Team(short_name=str(team[0]), long_name=str(team[2]))
		t.save()
		n += 1
	return HttpResponse('Loaded %d teams:' % n)

def update_records(request):
	return HttpResponse("Updated the teams's records")

@cache_page(60 * 5)
def standings(request):
	conn = httplib.HTTPSConnection("api.sportradar.us")
	conn.request("GET", "/nfl-ot1/seasontd/2016/standings.json?api_key=mk5mjt48drputswsxqct2uac")
	res = conn.getresponse()
	data = res.read()
	data = data.decode('utf-8')
	data = json.loads(data)
	return_string = ""

	for conference in data['conferences']:
		return_string = return_string + "<br/><br/>" + conference['name'] + "<br/><br/>"
		for division in conference['divisions']:
			return_string = return_string + "<br/><br/>" + division['name'] + "<br/><br/>"
			for team in division['teams']:
				return_string = return_string + team['name'] + " " + str(team['wins']) + "-" + str(team['losses']) + "<br/>"

	context = {'data': data}
	return render(request, 'nfl_scores/standings.html', context)

def get_teams(request):
	searchString = request.GET.get('searchString', None)

	# get the teams that match the search string
	teams = Team.objects.all().filter(long_name__contains=searchString)
	# need to convert teams to json
	returnTeams = [{'name': team.long_name} for team in teams]

	return JsonResponse({'teams': returnTeams})

# SportRadar API Key
# api_key=mk5mjt48drputswsxqct2uac
# consider making this a variable at the top of the file