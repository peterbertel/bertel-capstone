from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Team(models.Model):
	name = models.CharField(max_length=200, unique=True)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)

	def __str__(self):
		return 'The %s have %s wins and %s losses' % (self.name, self.wins, self.losses)

# class Week(models.Model):
# 	number = models.IntegerField(default=1)

# 	def __str__(self):
# 		return 'Week %s' % (self.number)

class Game(models.Model):
	# home and away team references are problematic
	home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_team", null=True)
	away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_team", null=True)
	week = models.IntegerField(default=1)
	home_score = models.IntegerField(default=0)
	away_score = models.IntegerField(default=0)
	# maybe can do home_score = away_score = models.IntegerField(default=0)
	# tied_game = models.BooleanField(default=False)

	# if home_score > away_score:
	# 	winner = models.ForeignKey(home_team, on_delete=models.CASCADE, related_name="winner", null=True)
	# 	loser = models.ForeignKey(away_team, on_delete=models.CASCADE, related_name="loser", null=True)
	# elif away_score > home_score:
	# 	winner = models.ForeignKey(away_team, on_delete=models.CASCADE, related_name="winner", null=True)
	# 	loser = models.ForeignKey(home_team, on_delete=models.CASCADE, related_name="loser", null=True)
	# else:
	# 	tied_game = True

	def __str__(self):
		# return 'The %s played the %s in week %s' (self.home_team, self.away_team, self.week)
		return 'Week: %s, The %s scored %s points against the %s, who scored %s points' % (self.week, self.home_team.name, \
			self.home_score, self.away_team.name, self.away_score)

