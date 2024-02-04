const avro = require("avro-js");

function bufferToCanvas(bytes, afWindow) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(new Blob([bytes], { type: "image/jpeg" }));
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      const canvas = document.createElement("canvas");
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      ctx.beginPath();
      ctx.strokeStyle = "green";
      ctx.rect(afWindow.x, afWindow.y, afWindow.w, afWindow.h);
      ctx.stroke();
      resolve(canvas);
    };
    img.src = url;
  });
}

function buildSensorsHtml(sensorReadings) {
  return Object.entries(sensorReadings).reduce(
    (acc, [name, value]) => `${acc}<p>${name}: ${value}</p>`,
    "",
  );
}

function start(requestSchemaJson, updateSchemaJson) {
  if ("WebSocket" in window) {
    const ws = new WebSocket(`ws://${window.location.host}/ws`);
    ws.binaryType = "arraybuffer";

    const requestType = avro.parse(JSON.parse(requestSchemaJson));
    const updateType = avro.parse(JSON.parse(updateSchemaJson));

    ws.onopen = function () {
      console.log(`Connected to WS`);
      document.getElementById("alwaysOn").onchange = function () {
        ws.send(requestType.toBuffer("SET_CAMERA_MODE_ALWAYS_ON"));
      };
      document.getElementById("automatic").onchange = function () {
        ws.send(requestType.toBuffer("SET_CAMERA_MODE_AUTOMATIC"));
      };
    };

    ws.onmessage = function (evt) {
      const update = updateType.fromBuffer(Buffer.from(evt.data));

      if (update.previewImage) {
        bufferToCanvas(update.previewImage.bytes, update.afWindow).then(
          (canvas) =>
            document.getElementById("preview").replaceChildren(canvas),
        );
      }

      document.getElementById(
        "space",
      ).innerText = `Space remaining: ${update.spaceRemaining} GiB`;

      document.getElementById("state").innerText = `State: ${update.state}`;

      document.getElementById("sensors").innerHTML = buildSensorsHtml(
        update.sensorReadings,
      );

      switch (update.cameraMode) {
        case "ALWAYS_ON":
          document.getElementById("alwaysOn").checked = true;
          break;

        case "AUTOMATIC":
          document.getElementById("automatic").checked = true;
          break;

        default:
          break;
      }
    };

    ws.onclose = function () {
      alert("Connection is closed...");
    };
  } else {
    alert("WebSocket NOT supported by your Browser!");
  }
}

window.start = start;
