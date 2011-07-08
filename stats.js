var plot, analysis_min, analysis_max;

$(function () {
  var overview;
  function refresh(ranges) {
    /** Refresh both plots when the user selects a time range to analyze. */
    
    var plot_options = {
        xaxis: { mode: "time" },
        selection: { mode: "x" },
        bars:{show:true,lineWidth:0.1,barWidth:24*3600*1000},
        series:{shadowSize:0,stack:true},
        grid: { hoverable: true,autoHighlight:false },
        legend:{container:"#legend"},
    };
    var new_options = {legend:{show:false},bars:{barWidth:28*24*3600*1000}};
    var overview_options = $.extend(true, {}, plot_options, new_options);

    data2 = {}
    if (ranges != undefined) {
      data2.min=Math.floor(ranges.xaxis.from/1000);
      data2.max=Math.floor(ranges.xaxis.to/1000);
    }
    
    $.getJSON("/stats/gettops", data2, function(data) {
      data2.tops = data;
      $.getJSON("/stats/costperday", data2, function(data) {
        plot = $.plot($("#placeholder"), data, plot_options);
      });
      $.getJSON("/stats/costpermonth", {tops:data}, function(data) {
        overview = $.plot($("#overview"), data, overview_options);
        if (ranges != undefined) {
          overview.setSelection(ranges, true);
        }
      });
    });
  }
  refresh();
  
  $("#placeholder,#overview").bind("plotselected", function (event, ranges) {
    refresh(ranges);
  });

  var prvMin, prvMax;
  $("#placeholder,#overview").bind("plothover", function (event, pos, item) {
    /**
    Refresh the call analysis table when the user hovers over a bar in one of
    the charts.
    */

    if (item) {
      var min = item.datapoint[0], max = new Date(min), source;
      switch (event.target.id) {
        case "placeholder":
          source = plot;
          max.setDate(max.getDate()+1)
          break;
        case "overview":
          source = overview;
          max.setMonth(max.getMonth()+1)
          break;
      }
      min = Math.floor(min/1000);
      max = Math.floor(max.getTime()/1000);
      
      if (min != prvMin || max != prvMax) {
        prvMin = min;
        prvMax = max;

        plot.unhighlight();
        overview.unhighlight();
        
        var series = source.getData();
        for (var i = 0; i < series.length; i++) {
          var points = series[i].datapoints.points;
          var ps = series[i].datapoints.pointsize;
          for (var j = 0; j < points.length; j+=ps) {
            if (points[j] == item.datapoint[0]) {
              source.highlight(i, [points[j],points[j+1],points[j+2]]);
            }
          }
        }
        
        analysis_min = min;
        analysis_max = max;
        refresh_analysis_table();
      }
    }
  });
  
  window.onresize = function() {
    /** Handle window resize events. */

    var height = $(window).height();
    height -= $("#contents").offset().top;
    height -= parseInt($("body").css("margin-bottom"));
    height -= parseInt($("#footer").css("margin-bottom"));
    height -= $("#footer").outerHeight();
    $("#contents").css("height",height);
  };
  window.onresize();
});

function edit(number,def) {
  /** Add a description for a telephone number into the database. */

  desc = prompt("Δώστε περιγραφή για τον αριθμό " + number, def);
  if (desc == null) {
    return;
  }
  $.post("/stats/addphone", {number:number,desc:desc}, function() {
    refresh_analysis_table();
  });
}

function refresh_analysis_table() {
  /**
  Retrieve and display the telephone calls made during a specified time period.
  */

  $.getJSON("/stats/getcalls", {min:analysis_min,max:analysis_max},
            function(data) {
    var text = "<table><tr><th style='width:14px'></th><th>Προορισμός</th><th>"+
               "Κόστος</th></tr>";
    var series = plot.getData(),color;
    for (var row in data) {
      for (var i = 0; i < series.length; ++i) {
        if (series[i].color == data[row][2]) {
          break;
        }
      }
      color = series[i==series.length ? i-1:i].color;
      if (data[row][3] == null) {
        tel = data[row][0];
      } else {
        tel = data[row][3];
      }
      text += "<tr><td><div style='width:4px;height:0;border:5px solid "+color+
              ";overflow:hidden;'></div></td><td><a href='javascript:edit(\""+
              data[row][0]+"\",\""+ (data[row][3] == null ? "" : data[row][3])+
              "\")'>[Αλλαγή]</a>" + tel + "</td><td>" + data[row][1] +
              "</td></tr>";
    }
    text += "</table>";
    $("#table-container").html(text);
  });
}

/* Workaround for a bug in displaying stacked charts in jQuery flot */
$.plot.plugins.push({
  init: function(plot) {
    function findMatchingSeries(s, allseries) {
      var res = null
      for (var i = 0; i < allseries.length; ++i) {
        if (s == allseries[i])
          break;
        
        if (allseries[i].stack == s.stack)
          res = allseries[i];
      }
      
      return res;
    }
    function stackData(plot, s, datapoints) {
      if (s.stack == null)
        return;

      var other = findMatchingSeries(s, plot.getData());
      if (!other)
        return;

      var points = datapoints.points;
      var otherpoints = other.datapoints.points;
      var tmp = [], i = 0, j = 0;
      while (i < points.length && j < otherpoints.length) {
        if (points[i] > otherpoints[j]) {
          tmp.push(otherpoints[j]);
          tmp.push(0);
          tmp.push(0);
          j+=3;
        } else {
          if (points[i] == otherpoints[j]) {
            j+=3;
          }
          tmp.push(points[i++]);
          tmp.push(points[i++]);
          tmp.push(points[i++]);
        }
      }
      while (i < points.length) {
        tmp.push(points[i++]);
        tmp.push(points[i++]);
        tmp.push(points[i++]);
      }
      while (j < otherpoints.length) {
        tmp.push(otherpoints[j]);
        tmp.push(0);
        tmp.push(0);
        j+=3;
      }
      datapoints.points = tmp;
    };
    
    var tmp = plot.hooks.processDatapoints.pop();
    plot.hooks.processDatapoints.push(stackData);
    plot.hooks.processDatapoints.push(tmp);
  }
});
