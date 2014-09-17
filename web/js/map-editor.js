// global variables
var regions, bases, events;
// raphael
var raphael = Raphael("svg-map");
// angular.js
var MapEditor = angular.module('MapEditor', ['ngRoute']);

var width = 2000;
var height = 1160;
var offsetX = 155;
var offsetY = 135;

var hRatio = (width - offsetX) / 360;
var vRatio = (height - offsetY)  / 180;

// ---{{{
  
  // function map2real(x, y) {
  //   return {
  //     "x": x / hRatio,
  //     "y": y / vRatio
  //   }
  // }

  function real2map(x, y) {
    return {
      "x": width - (x * hRatio),
      "y": y * vRatio
    }
  }

  document.oncontextmenu = function (e) {
    if(e.target.hasAttribute('right-click')) {
      return false;
    }
  };

  // loading data
  $(function(){
    $.getJSON("data.json", function(data) {
      
      // process each key and val
      $.each(data, function(key, val) {
        if (key === "regions")
          regions = val;
        else if (key === "events")
          events = val;
        else if (key === "bases")
          bases = val;
      });

      // initialize the map with current data
      for (var regionKey in regions) {
        // if (regionKey != "NA" || regionKey != "SA") continue;

        var region = regions[regionKey];

        // load all bases from this region
        for (var baseKey in region.bases) {
          var base = region.bases[baseKey];
          var mapBase = new Base(raphael, bases[baseKey], regionKey);
          var point = real2map(base["x"], base["y"])
          mapBase.setPosition(point["x"], point["y"]);
        }

        // load all events from this region
        for (var eventKey in region.events) {
          var event = region.events[eventKey];
          var mapEvent = new Event(raphael, events[eventKey], regionKey);
          var point = real2map(event["x"], event["y"])
          mapEvent.setPosition(point["x"], point["y"]);
        }
      }

    });
  });
//---}}}


/*************
 *  Classes  *
 *************/
//---{{{
  var baseColor = "#FFA500";
  var eventColor = "#4C4CFF";
  var showAnim = Raphael.animation({opacity: 1}, 2e2);
  var hideAnim = Raphael.animation({opacity: 0}, 2e2);

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
    this.color = color;
    this.innerRadius = innerRadius;
    this.outerRadius = outerRadius;
    this.circle = null;
  }

  Node.prototype.setPosition = function(x, y) 
  {
    // create the circle if not created
    if (this.circle === null)
      this.circle = this.graphics.circle(x, y, this.innerRadius);

    // setting attributes
    this.circle.attr({ "cx": x, "cy": y, "opacity": 0, "fill": this.color, "stroke": "#FFFFFF" });
    this.circle.glow({ width: this.outerRadius, color: "#FFFFFF" });
    this.circle.animate(showAnim);
  }

  // Base class
  function Base(graphics, title, region)
  {
    Node.call(this, graphics, title, region, "bases", baseColor, 8, 8);
  }
  Base.prototype = Object.create(Node.prototype);
  Base.prototype.constructor = Base;

  // Event class
  function Event(graphics, title, region)
  {
    Node.call(this, graphics, title, region, "events", eventColor, 8, 8);
  }
  Event.prototype = Object.create(Node.prototype);
  Event.prototype.constructor = Event;
//---}}}

/****************
 *  angular.js  *
 ****************/
// ---{{{
  
  // right click directive
  MapEditor.directive('ngRightClick', function($parse) {
    return function(scope,element,attrs){
      var fn = $parse(attrs.ngRightClick);
      console.log (fn);
      element.bind('contextmenu',function(event){
        scope.$apply(function() {
          event.preventDefault();
          fn(scope, {$event: event});
        });
        return false;
      }) ;
    }
  });
  
  MapEditor.controller("MapEditorController", function($scope) {

    $scope.coordinate = { x: "0", y: "0" };

    // mouse moving action
    $scope.showCoordinate = function($event) {
      $scope.coordinate.x = $event.offsetX;
      $scope.coordinate.y = $event.offsetY;
    }

    // mouse click action
    $scope.addBase = function($event) {
      var base = new Base(raphael, "B1", "NA");
      base.setPosition($event.offsetX, $event.offsetY);
    }

    // mouse click action
    $scope.addEvent = function($event) {
      var event = new Event(raphael, "B1", "NA");
      event.setPosition($event.offsetX, $event.offsetY);
    }

  });
//---}}}
