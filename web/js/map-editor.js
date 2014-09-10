var MapEditor = angular.module('MapEditor', ['ngRoute']);

MapEditor.controller("MapEditorController", function($scope) {
  // testing code function
  $scope.showCoordinate = function($event) {
    console.log ($event.offsetX + ", " + $event.offsetY);
  }

});
