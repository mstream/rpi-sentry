const avro = require("avro-js");

function bufferToImage(bytes) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(new Blob([bytes], { type: "image/jpeg" }));
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.src = url;
  });
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
      console.log("new preview frame received");
      const update = updateType.fromBuffer(Buffer.from(evt.data));
      if (update.previewImage) {
        bufferToImage(update.previewImage.bytes).then((img) =>
          document.getElementById("preview").replaceChildren(img),
        );
      }
      document.getElementById("state").innerText = `State: ${update.state}`;
      document.getElementById(
        "space",
      ).innerText = `Space remaining: ${update.spaceRemaining} GiB`;

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
