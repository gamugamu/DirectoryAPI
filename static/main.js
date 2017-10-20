(function () {

  'use strict';

  angular.module('Directory-api', [])

  .controller('Directory-api-controller', ['$scope', '$log', '$http',
    function($scope, $log, $http) {

    $scope.perform_api_test = function() {
      $http.post('/starttest').
        success(function(results) {
          $log.log(results);
        }).
        error(function(error) {
          $log.log(error);
        });
    };
  }
  ]);

}());
