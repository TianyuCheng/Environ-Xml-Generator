// global variables
var regions, bases, events;
// raphael
var raphael = Raphael("svg-map");
// angular.js
var MapEditor = angular.module('MapEditor', ['ngRoute']);
// operation stack
var stack = new Array();
var current = null;

var width = 2000;
var height = 1160;
var offsetX = 155;
var offsetY = 135;

var hRatio = (width - offsetX) / 360;
var vRatio = (height - offsetY)  / 180;

// ---{{{
  
  function map2real(x, y) {
    return {
      "x": (width - x) / hRatio,
      "y": y / vRatio
    };
  }

  function real2map(x, y) {
    return {
      "x": width - (x * hRatio),
      "y": y * vRatio
    };
  }

  function inRange(x, y) {
    var point = map2real(x, y);
    x = point.x;
    y = point.y;
    if (x <= 0 || x >= 355 || y <= 10 || y >= 165) 
      return false;
    return true;
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
        if (key === "regions") {
          regions = val;
          // initialize regions in select
          var select = $("#region-select");
          for (var initials in regions)
            $('<option value="' + initials+ '">' + initials+ '</option>').appendTo(select);
        }
        else if (key === "events") {
          events = val;
          // initialize events in select
          var select = $("#event-select");
          for (var key in events)
            $('<option value="' + key+ '">' + events[key]+ '</option>').appendTo(select);
        }
        else if (key === "bases") {
          bases = val;
          // initialize bases in select
          var select = $("#base-select");
          for (var key in bases)
            $('<option value="' + key+ '">' + bases[key]+ '</option>').appendTo(select);
        }
      });

      // initialize the map with current data
      for (var regionKey in regions) {
        // if (regionKey != "NA" || regionKey != "SA") continue;

        var region = regions[regionKey];

        // load all bases from this region
        for (var baseKey in region.bases) {
          var base = region.bases[baseKey];
          var mapBase = new Base(raphael, baseKey, regionKey);
          var point = real2map(base["x"], base["y"])
          mapBase.setPosition(point["x"], point["y"]);
        }

        // load all events from this region
        for (var eventKey in region.events) {
          var event = region.events[eventKey];
          var mapEvent = new Event(raphael, eventKey, regionKey);
          var point = real2map(event["x"], event["y"])
          mapEvent.setPosition(point["x"], point["y"]);
        }
      }

    });
  });
//---}}}

/*************************
 *  js plugin for popup  *
 *************************/
//---{{{

  $("#save").on("click", function(){
    console.log("save point " + current.circle.node.raphaelid);
    // save the points
    current.region = $("#region-select").val();
    if (current.type === "bases")
      current.title = $("#base-select").val();
    else 
      current.title = $("#event-select").val();
    $("#overlay").click();  // unfocus
  });

  $("#delete").on("click", function(){
    console.log("delete point " + current.circle.node.raphaelid);
    current.destroy();
    $("#overlay").click();  // unfocus
  });

  $("#close").on("click", function(){
    $("#overlay").click();
  });

  $("#overlay").on({
    "click": function() {
      $("#popup").fadeOut(200);
    }
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

  Node.prototype.setPosition = function(x, y) {
    // create the circle if not created
    if (this.circle === null) {
      this.circle = this.graphics.circle(x, y, this.innerRadius);
      this.popup(); // register popup
    }

    // setting attributes
    this.circle.attr({ "cx": x, "cy": y, "opacity": 0, "fill": this.color, "stroke": "#FFFFFF" });
    this.glow = this.circle.glow({ width: this.outerRadius, color: "#FFFFFF" });
    this.circle.animate(showAnim);
  }

  Node.prototype.destroy = function() {
    this.circle.remove();
    this.glow.remove();
  }

  Node.prototype.popup = function() {
    var that = this;
    var node = $(this.circle.node);
    node.on("click", function(event){
      current = that;
      $("#popup").fadeIn(200);  // fade in popup

      // set up values
      var region_select = $("#region-select");
      var base_select = $("#base-select");
      var event_select = $("#event-select");

      region_select.val(that.region);

      if (that.type === "bases") {
        $("#base-select-div").show();
        base_select.prop('disabled', false);
        event_select.prop("disabled", "disabled");
        $("#event-select-div").hide();

        base_select.val(that.title);
      }
      else {
        $("#event-select-div").show();
        event_select.prop('disabled', false);
        base_select.prop("disabled", "disabled");
        $("#base-select-div").hide();

        event_select.val(that.title);
      }
      
      event.preventDefault();
      return false;
    });
  }

  // Base class
  function Base(graphics, title, region)
  {
    Node.call(this, graphics, title, region, "bases", baseColor, 10, 10);
  }
  Base.prototype = Object.create(Node.prototype);
  Base.prototype.constructor = Base;

  // Event class
  function Event(graphics, title, region)
  {
    Node.call(this, graphics, title, region, "events", eventColor, 10, 10);
  }
  Event.prototype = Object.create(Node.prototype);
  Event.prototype.constructor = Event;
//---}}}

/****************
 *  angular.js  *
 ****************/
// ---{{{

  // right click on map
  MapEditor.directive('ngRightClick', function($parse) {
    return function(scope, element, attrs){
      var fn = $parse(attrs.ngRightClick);
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
      if (inRange($event.offsetX, $event.offsetY)) {
        console.log ("in");
        var base = new Base(raphael, "B1", "NA");
        base.setPosition($event.offsetX, $event.offsetY);
        stack.push(base);
      }
      else {
        console.log("base out of the map!");
      }
    }

    // mouse click action
    $scope.addEvent = function($event) {
      if (inRange($event.offsetX, $event.offsetY)) {
        var event = new Event(raphael, "B1", "NA");
        event.setPosition($event.offsetX, $event.offsetY);
        stack.push(event);
      }
      else {
        console.log("event out of the map!");
      }
    }

    $scope.exports = function() {
      console.log ("exporting data");
    }

  });
//---}}}
