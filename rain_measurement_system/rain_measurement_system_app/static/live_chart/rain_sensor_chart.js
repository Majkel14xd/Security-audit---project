window.onload = function rain_sensor_chart() {
  var data_in_chart = [];
  var chart = new CanvasJS.Chart("live_graph", {
    title: {
      text: "Czujnik deszczu",
    },
    axisX: {
      title: "Godzina",
      valueFormatString: "HH:mm:ss",
    },
    axisY: {
      title: "Wartość",
      minimum: 0,
      maximum: 4095,
    },
    data: [
      {
        type: "line",
        dataPoints: data_in_chart,
      },
    ],
  });

  var rain_sensor_chart_update = function () {
    var updateInterval = 10000;
    var dataLength = 12;
    $.ajax({
      url: "/rain_sensor_data/",
      type: "GET",
      dataType: "json",
      success: function (data) {
        const rain_sensor_data = data.get_rain_sensor_data;

        var now = new Date();
        data_in_chart.push({
          x: now,
          y: rain_sensor_data,
        });

        if (data_in_chart.length > dataLength) {
          data_in_chart.shift();
        }

        chart.render();
      },
      complete: function () {
        setTimeout(rain_sensor_chart_update, updateInterval);
      },
    });
  };

  rain_sensor_chart_update();
};
