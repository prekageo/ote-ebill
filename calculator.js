$(function () {
  $("#datepicker-from").datepicker({ dateFormat: "dd/mm/yy" });
  $("#datepicker-to").datepicker({ dateFormat: "dd/mm/yy" });
  
  /* Select previous month */
  var date_from = new Date();
  var date_to = new Date();
  date_from.setDate(1);
  date_from.setMonth(date_from.getMonth()-1);
  date_to.setDate(0);
  $("#datepicker-from").datepicker("setDate",date_from);
  $("#datepicker-to").datepicker("setDate",date_to);
  
  $("#button").click(function() {
    $("#placeholder").html("<img src=\"images/ajax-loading.gif\">");
    $("#results").fadeIn(3000);
    var min = $("#datepicker-from").datepicker("getDate").getTime()/1000;
    var max = $("#datepicker-to").datepicker("getDate").getTime()/1000;
    $.getJSON("/calculator/calculate", {"min":min,"max":max}, function(data) {
      var text = "<table><tr><th>Σύνολο</th><th>Εταιρεία</th><th>Πρόγραμμα"+
                 "</th><th>Τέλη</th><th>Αστικές</th><th>Υπεραστικές</th><th>"+
                 "Κινητά</th></tr>";
      for (var row in data) {
        text += "<tr><td class=\"r\">"+data[row][2]["total"]+"</td><td style="+
                "\"height:25px;background:url('"+data[row][1]+"') no-repeat "+
                "scroll 50% 50% transparent;\"></td><td>"+data[row][0]+"</td>"+
                "<td class=\"r\">"+data[row][2]["monthly_charges"]+"</td><td "+
                "class=\"r\">"+data[row][2]["local"]+"</td><td class=\"r\">"+
                data[row][2]["long_distance"]+"</td><td class=\"r\">"+
                data[row][2]["mobile"]+"</td></tr>";
      }
      text += "</table>";
      $("#placeholder").html(text);
    });
    return false;
  });
});
