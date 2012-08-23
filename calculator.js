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

  $(".tab-header input[type=radio]").change(function() {
    var selected_tab = $(":checked").index(".tab-header input[type=radio]");
    $(".tab").hide();
    $(".tab").eq(selected_tab).show();
  });

  $("#button").click(function() {
    $("#placeholder,#overview").html("<img src=\"images/ajax-loading.gif\">");
    $("#results").fadeIn(3000);
    var min = $("#datepicker-from").datepicker("getDate").getTime()/1000;
    var max = $("#datepicker-to").datepicker("getDate").getTime()/1000;
    var datasource = $("#datasource-db")[0].checked ? "D" :
        $("#datasource-csv")[0].checked ? "C" : null;
    var params = {
      "datasource":datasource,
    };
    switch (datasource) {
      case "D":
        params.min = min;
        params.max = max;
        break;
      case "C":
        params.csv = $("#csv").val();
        break;
    }
    $.getJSON("/calculator/calculate", params, function(data) {
      if (data == null) {
        $("#overview").html("Δε βρέθηκαν κλήσεις.");
        $("#placeholder").html("");
        return;
      }
      var text = "<table><tr><th>Σύνολο</th><th>Εταιρεία</th><th>Πρόγραμμα"+
                 "</th><th>Τέλη</th><th>Χρονοχρέωση</th><th>Αστικές</th><th>Υπεραστικές</th><th>"+
                 "Κινητά</th></tr>";
      var invoices = data.invoices;
      for (var row in invoices) {
        text += "<tr>";
        text += "<td class=\"r\">"+invoices[row][2]["total"]+"</td>";
        text += "<td style=\"height:25px;background:url('"+invoices[row][1]+"') no-repeat scroll 50% 50% transparent;\"></td>";
        text += "<td>"+invoices[row][0]+"</td>";
        text += "<td class=\"r\">"+invoices[row][2]["monthly_charges"]+"</td>";
        text += "<td>"+invoices[row][2]["time_based_charges"]+"</td>";
        text += "<td class=\"r\">"+invoices[row][2]["local"]+"</td>";
        text += "<td class=\"r\">"+invoices[row][2]["long_distance"]+"</td>";
        text += "<td class=\"r\">"+invoices[row][2]["mobile"]+"</td>";
        text += "</tr>";
      }
      text += "</table>";
      $("#placeholder").html(text);

      function category_line(category) {
        return "πλήθος: " + category.count + ", διάρκεια: " + Math.round(category.duration/60)+"', κόστος: &euro; "+category.cost;
      }
      
      var text = "<table>";
      text += "<tr><th>Πλήθος κλήσεων</th><td>"+data.overview.count_calls+"</td></tr>";
      text += "<tr><th>Αστικές κλήσεις</th><td>"+category_line(data.overview.local)+"</td></tr>";
      text += "<tr><th>Υπεραστικές κλήσεις</th><td>"+category_line(data.overview.long_distance)+"</td></tr>";
      text += "<tr><th>Κλήσεις προς κινητά</th><td>"+category_line(data.overview.mobile)+"</td></tr>";
      text += "<tr><th>Λοιπές κλήσεις</th><td>"+category_line(data.overview.other)+"</td></tr>";
      text += "<tr><th>Πρώτη κλήση</th><td>"+new Date(data.overview.first_call_timestamp*1000).toLocaleString()+"</td></tr>";
      text += "<tr><th>Τελευταία κλήση</th><td>"+new Date(data.overview.last_call_timestamp*1000).toLocaleString()+"</td></tr>";
      text += "<tr><th>Ημέρες</th><td>"+data.overview.count_days+"</td></tr>";
      text += "<tr><th>Κλήσεις που αγνοήθηκαν</th><td>"+category_line(data.overview.skipped)+", λίστα: "+data.overview.skipped.list+"</td></tr>";
      text += "</table>";
      $("#overview").html(text);
    });
    return false;
  });
});
