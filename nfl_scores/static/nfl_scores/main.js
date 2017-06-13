var app = angular.module("nflScoresApp", []);
app.controller("weekCtrl", function($scope, $http) {
	$scope.week = 1;
	$scope.totalWeeks = 17;
	$scope.games = [];
	$scope.searchString = "";
	$scope.teams = new Set();

	$scope.nextWeek = function() {
		if ($scope.week < $scope.totalWeeks) {
			$scope.week++;
			$scope.updateGames($scope.week);
		}
	}

	$scope.previousWeek = function() {
		if ($scope.week > 1) {
			$scope.week--;
			$scope.updateGames($scope.week);
		}
	}

	$scope.changeWeek = function(weekNumber) {
		$scope.week = weekNumber;
		$scope.updateGames($scope.week);
	}

	$scope.getNumWeeks = function() {
		return new Array($scope.totalWeeks);
	}

	$scope.updateGames = function(weekNumber) {

		$http({
			method: 'GET',
			url: '/get_games?week=' + weekNumber
		}).then(function successCallback(response) {
			$scope.games = response.data.games;
			$scope.createTeamSet();
		}, function errorCallback(response) {
			console.log("failed to get the data");
		});
	}

	$scope.createTeamSet = function() {
		for (var i = 0; i < $scope.games.length; i++) {
			game = $scope.games[i];
			$scope.teams.add(game.home_team);
			$scope.teams.add(game.away_team);
		}
	}

	$scope.showQuarterPoints = function(game) {

		away_team = game.away_team;
		home_team = game.home_team;

		if (game.show_quarter_points) {
			game.show_quarter_points = false;
		}
		else {
			game.show_quarter_points = true;
		}
	}

	$scope.searchStringIsATeam = function() {
		s = $scope.searchString.charAt(0).toUpperCase() + $scope.searchString.slice(1);
		return $scope.teams.has(s);
	}

	$scope.updateGames($scope.week);
});