from django.shortcuts import render
from django.http import HttpResponse

from .models import Team, Game

import nflgame

def week_view(request):
	w = int(request.GET.get('w', 1))

	teams = Team.objects.all()
	games = Game.objects.filter(week=w)

	context = {'games': games, 'week': w}

	return render(request, 'nfl_scores/week_view.html', context)

def load_games(request):
	# check if there are games for the given weeks
		#basically, see if there is any updated nfl game data you need to load into your db
	# use the nflgame module to load in the games you don't have
	# if it is a week that has not happened yet, populate the data with an external api

	# How do I check if a game already exists in the db?
	# Also, how do I update a game in the database? Like the chiefs and raiders game


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

def standings(request):
	import httplib
	import json
	conn = httplib.HTTPSConnection("api.sportradar.us")
	conn.request("GET", "/nfl-ot1/seasontd/2016/standings.json?api_key=mk5mjt48drputswsxqct2uac")
	res = conn.getresponse()
	data = res.read()
	data = data.decode('utf-8')
	# import pdb; pdb.set_trace()
	data = json.loads(data)
	# x['conferences'][0]['divisions'][0]['name']
	# AFC East
	return_string = ""
	# only do the following if it has not been stored in cache

	for conference in data['conferences']:
		return_string = return_string + "<br/><br/>" + conference['name'] + "<br/><br/>"
		for division in conference['divisions']:
			return_string = return_string + "<br/><br/>" + division['name'] + "<br/><br/>"
			for team in division['teams']:
				return_string = return_string + team['name'] + " " + str(team['wins']) + "-" + str(team['losses']) + "<br/>"

	return HttpResponse("Standings page: <br/>" + return_string)

# Using the SportRadar API
# import http.client

# conn = http.client.HTTPSConnection("api.sportradar.us")

# conn.request("GET", "/nfl-ot1/games/b7aeb58f-7987-4202-bc41-3ad9a5b83fa4/pbp.xml?api_key={mk5mjt48drputswsxqct2uac}")

# res = conn.getresponse()
# data = res.read()

# print(data.decode("utf-8"))