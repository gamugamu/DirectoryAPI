(function () {

  'use strict';

  angular.module('WordcountApp', [])

  .controller('WordcountController', ['$scope', '$log', '$http',
    function($scope, $log, $http) {

    $scope.getResults = function() {
      // get the URL from the input
      var userInput = $scope.url;
      $scope.result = ""
      // fire the API request
      $http.post('/start', {"url": userInput}).
        success(function(results) {
          $log.log(results);
          $scope.result = results
        }).
        error(function(error) {
          $log.log(error);
        });

    };

  }
  ]);

}());
