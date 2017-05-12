from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse

# per-view caching found from
#	 https://docs.djangoproject.com/en/1.10/topics/cache/
from django.views.decorators.cache import cache_page

from .models import Conference, Division, Team, Game

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
				# either it is (1) a future week or (2) a past week and the team is on bye
				games = Game.objects.filter(week=w)
				if len(games) == 0:
					future_games = get_future_games(w, team.long_name)
					if len(future_games) == 0:
						context = {'games': games, 'week': w, 'team':t, 'future_games': future_games}
						return render(request, 'nfl_scores/week_view.html', context)
				else:
					context = {'games': game, 'week': w, 'team':t, 'future_games': future_games}
					return render(request, 'nfl_scores/week_view.html', context)
		games = game
	else:
		games = Game.objects.filter(week=w)
		if len(games) == 0:
			future_games = get_future_games(w)

	context = {'games': games, 'week': w, 'team':t, 'future_games': future_games}

	return render(request, 'nfl_scores/week_view.html', context)

def get_future_games(week, team=''):
	conn = httplib.HTTPSConnection("api.sportradar.us")
	conn.request("GET", "/nfl-ot1/games/2016/reg/schedule.json?api_key=wnvqxfwz8v8ghu49ycapv3ww")
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
def load_weekly_games(request):
	n = 0
	w = int(request.GET.get('w', 1))
	if len(Game.objects.filter(week=w)) == 0:
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

			g = Game(home_team=home_team, away_team=away_team, week=w, home_score=game.score_home, away_score=game.score_away, \
				home_points_q1=game.score_home_q1, home_points_q2=game.score_home_q2, home_points_q3=game.score_home_q3, \
				home_points_q4=game.score_home_q4, away_points_q1=game.score_away_q1, away_points_q2=game.score_away_q2, \
				away_points_q3=game.score_away_q3, away_points_q4=game.score_away_q4)

			g.save()
			n += 1

	return HttpResponse('Loaded %d games' % n)


@cache_page(60 * 5)
def standings(request):
	data = {}

	data['conferences'] = []
	conferences = Conference.objects.all()
	conference_count = 0
	for conference in conferences:
		c = {'name' : conference.conference_name, 'divisions' : []}
		data['conferences'].append(c)
		division_count = 0
		for division in Division.objects.filter(conference=conference):
			d = {'name': division.division_name, 'teams': []}
			data['conferences'][conference_count]['divisions'].append(d)
			for team in Team.objects.filter(division=division):
				t = {'name': team.long_name, 'wins': team.wins, 'losses': team.losses, 'ties':team.ties}
				data['conferences'][conference_count]['divisions'][division_count]['teams'].append(t)
			division_count += 1
		conference_count += 1

	context = {'data': data}
	return render(request, 'nfl_scores/standings.html', context)

def get_teams(request):
	searchString = request.GET.get('searchString', None)

	# get the teams that match the search string
	teams = Team.objects.all().filter(long_name__contains=searchString)
	# need to convert teams to json
	returnTeams = [{'name': team.long_name} for team in teams]

	return JsonResponse({'teams': returnTeams})

def load_all_games(request):
	n = 0
	for w in range(16):
		games = nflgame.games(2016, week=w+1)
		if len(games) == 0:
			break
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

			g = Game(home_team=home_team, away_team=away_team, week=w+1, home_score=game.score_home, away_score=game.score_away, \
				home_points_q1=game.score_home_q1, home_points_q2=game.score_home_q2, home_points_q3=game.score_home_q3, \
				home_points_q4=game.score_home_q4, away_points_q1=game.score_away_q1, away_points_q2=game.score_away_q2, \
				away_points_q3=game.score_away_q3, away_points_q4=game.score_away_q4)

			g.save()
			n += 1

	return HttpResponse('Loaded %d games' % n)

def load_sportradar_data(request):
	'''
	This view loads in the data for Conferences, Divisions, and Teams in each Division.
	'''
	conn = httplib.HTTPSConnection("api.sportradar.us")
	conn.request("GET", "/nfl-ot1/seasontd/2016/standings.json?api_key=wnvqxfwz8v8ghu49ycapv3ww")
	res = conn.getresponse()
	data = res.read()
	data = data.decode('utf-8')
	data = json.loads(data)

	for conference in data['conferences']:
		c = Conference(conference_name=conference['name'])
		c.save()
		for division in conference['divisions']:
			d = Division(division_name=division['name'], conference=c)
			d.save()
			for team in division['teams']:
				team_name = team['name']
				if "New York" in team_name:
					team_name = team_name.split()[-1]
				t = Team(division=d, short_name=team['alias'], long_name=team_name, \
					wins=team['wins'], losses=team['losses'], ties=team['ties'])
				t.save()

	return HttpResponse('Loaded sportradar data')

def get_quarter_points(request):
	home_team_name = request.GET.get('home_team', None)
	away_team_name = request.GET.get('away_team', None)
	week = request.GET.get('week', None)

	home_team = Team.objects.all().filter(long_name__contains=home_team_name)
	away_team = Team.objects.all().filter(long_name__contains=away_team_name)
	game = Game.objects.filter(week=week).filter(home_team=home_team).filter(away_team=away_team)[0]
	points_per_quarter = {
		'home_q1': game.home_points_q1,
		'home_q2': game.home_points_q2,
		'home_q3': game.home_points_q3,
		'home_q4': game.home_points_q4,
		'away_q1': game.away_points_q1,
		'away_q2': game.away_points_q2,
		'away_q3': game.away_points_q3,
		'away_q4': game.away_points_q4
	}

	return JsonResponse({'points_per_quarter': points_per_quarter})


# SportRadar API Key:
# wnvqxfwz8v8ghu49ycapv3ww