import { BLYNK_AUTH_TOKEN } from "./password_keys.js";
let RAIN_SENSOR_POWER_ON_OFF = "V1";
let WATER_SENSOR_POWER_ON_OFF = "V0";
function updateSwitchState(toggleSwitch, powerOnOff) {
  toggleSwitch.addEventListener("change", function () {
    const isChecked = toggleSwitch.checked;
    const apiUrl = isChecked
      ? `https://blynk.cloud/external/api/update?token=${BLYNK_AUTH_TOKEN}&${powerOnOff}=1`
      : `https://blynk.cloud/external/api/update?token=${BLYNK_AUTH_TOKEN}&${powerOnOff}=0`;

    fetch(apiUrl)
      .then((response) => {
        if (!response.ok) {
        }
      })
      .catch((error) => {});
  });
}

function checkBlynkAPI(switchElement, powerOnOff) {
  $.get(
    `https://blynk.cloud/external/api/get?token=${BLYNK_AUTH_TOKEN}&${powerOnOff}`,
    function (data) {
      switchElement.prop("checked", data != 0);
    }
  );
}

$(document).ready(function () {
  const rainSensorSwitch = $("#switch_rain_sensor_off_on");
  const waterSensorSwitch = $("#switch_water_sensor_off_on");

  updateSwitchState(rainSensorSwitch[0], RAIN_SENSOR_POWER_ON_OFF);
  updateSwitchState(waterSensorSwitch[0], WATER_SENSOR_POWER_ON_OFF);

  checkBlynkAPI(rainSensorSwitch, RAIN_SENSOR_POWER_ON_OFF);
  checkBlynkAPI(waterSensorSwitch, WATER_SENSOR_POWER_ON_OFF);

  setInterval(function () {
    checkBlynkAPI(rainSensorSwitch, RAIN_SENSOR_POWER_ON_OFF);
    checkBlynkAPI(waterSensorSwitch, WATER_SENSOR_POWER_ON_OFF);
  }, 1000);
});
