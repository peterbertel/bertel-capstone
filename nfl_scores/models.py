from __future__ import unicode_literals

from django.db import models

import uuid

class Conference(models.Model):
	conference_name = models.CharField(max_length=200, unique=True)

	def __str__(self):
		return '%s' % (self.conference_name)

class Division(models.Model):
	division_name = models.CharField(max_length=200, unique=True)
	conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name="conference", null=True)

	def __str__(self):
		return '%s - %s' % (self.division_name, self.conference.conference_name)


class Team(models.Model):
	division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="division", null=True)
	short_name = models.CharField(max_length=200, unique=True)
	long_name = models.CharField(max_length=200, unique=True)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	ties = models.IntegerField(default=0)

	def __str__(self):
		return '%s - %s' % (self.short_name, self.long_name)

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

