from __future__ import unicode_literals

from django.db import models

import uuid

class Team(models.Model):
	short_name = models.CharField(max_length=200, unique=True)
	long_name = models.CharField(max_length=200, unique=True)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)

	def __str__(self):
		return 'The %s have %s wins and %s losses' % (self.long_name, self.wins, self.losses)

class Game(models.Model):
	home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="home_team", null=True)
	away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="away_team", null=True)
	week = models.IntegerField(default=1)
	home_score = models.IntegerField(default=0)
	home_points_q1 = models.IntegerField(default=0)
	home_points_q2 = models.IntegerField(default=0)
	home_points_q3 = models.IntegerField(default=0)
	home_points_q4 = models.IntegerField(default=0)

	away_score = models.IntegerField(default=0)
	away_points_q1 = models.IntegerField(default=0)
	away_points_q2 = models.IntegerField(default=0)
	away_points_q3 = models.IntegerField(default=0)
	away_points_q4 = models.IntegerField(default=0)

	def __str__(self):
		return 'Week: %s, The %s scored %s points against the %s, who scored %s points' % (self.week, self.home_team.long_name, \
			self.home_score, self.away_team.long_name, self.away_score)

