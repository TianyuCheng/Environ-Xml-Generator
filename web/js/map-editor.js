// global variables
var regions, bases, events;

// raphael
var raphael = Raphael("svg-map");

// angular.js
var MapEditor = angular.module('MapEditor', ['ngRoute']);

// loading data
$(function(){
  $.getJSON("data.json", function(data) {
    $.each(data, function(key, val) {
      if (key === "regions")
        regions = val;
      else if (key === "events")
        events = val;
      else if (key === "bases")
        bases = val;
    });

    var base = new Base(raphael, "B1", "NA");
    base.add(100, 100);
  });
});

// BaseNode class
function Node(graphics, title, region, type, color, innerRadius, outerRadius)
{
  // regions sanity check
  if (!(region in regions))
  {
    alert("region [" + region + "] has not been found in regions");
    console.log (region);
    console.log (regions);
  }

  // initialization
  this.graphics = graphics;
  this.title = title;
  this.region = region;
  this.type = type;
  this.color = "#ffff00";
  this.innerRadius = 10;
  this.outerRadius = 5;
}

Node.prototype.add = function(x, y) 
{
  // Creates circle at x = 50, y = 40, with radius 10
  var circle = this.graphics.circle(x, y, this.innerRadius);
  // Sets the fill attribute of the circle to red (#f00)
  circle.attr("fill", "#f00");
  // Sets the stroke attribute of the circle to white
  circle.attr("stroke", "#fff");
  console.log(circle);
}

// Base class
function Base(graphics, title, region)
{
  Node.call(this, graphics, title, region, "bases", "#ffff00", 10, 5);
}
Base.prototype = Object.create(Node.prototype);
Base.prototype.constructor = Base;



// angular.js
MapEditor.controller("MapEditorController", function($scope) {

  $scope.coordinate = { x: "0", y: "0" };

  // mouse moving action
  $scope.showCoordinate = function($event) {
    $scope.coordinate.x = $event.offsetX;
    $scope.coordinate.y = $event.offsetY;
  }

  // mouse click action
  $scope.addStuff = function($event) {
    var base = new Base(raphael, "B1", "NA");
    base.add($event.offsetX, $event.offsetY);
  }

});
