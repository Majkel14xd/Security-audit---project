window.onload = function rain_gauge_chart() {
  var data_in_chart = [];
  var chart = new CanvasJS.Chart("live_graph", {
    title: {
      text: "Czujnik wody po opadach",
    },
    axisX: {
      title: "Godzina",
      valueFormatString: "HH:mm:ss",
    },
    axisY: {
      title: "Wartość",
      minimum: 0,
      maximum: 100,
    },
    data: [
      {
        type: "line",
        dataPoints: data_in_chart,
      },
    ],
  });

  var rain_gauge_chart_update = function () {
    var updateInterval = 30000;
    var dataLength = 12;
    $.ajax({
      url: "/rain_gauge_data/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        const rain_gauge_data = data.get_rain_gauge_data;

        var now = new Date();
        data_in_chart.push({
          x: now,
          y: rain_gauge_data,
        });

        if (data_in_chart.length > dataLength) {
          data_in_chart.shift();
        }

        chart.render();
      },
      complete: function () {
        setTimeout(rain_gauge_chart_update, updateInterval);
      },
    });
  };

  rain_gauge_chart_update();
};
