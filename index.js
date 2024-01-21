const avro = require("avro-js");

function bufferToImage(bytes) {
  return new Promise((resolve) => {
    const url = URL.createObjectURL(new Blob([bytes], { type: "image/jpeg" }));
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      resolve(img);
    };
    img.style = "height:50%;";
    img.src = url;
  });
}

function start(schemaJson) {
  console.log(`SCHEMA: ${schemaJson}`);
  if ("WebSocket" in window) {
    const ws = new WebSocket(`ws://${window.location.host}/ws`);
    ws.binaryType = "arraybuffer";

    const updateType = avro.parse(JSON.parse(schemaJson));

    ws.onopen = function () {
      console.log(`Connected to WS`);
    };

    ws.onmessage = function (evt) {
      console.log("new preview frame received");
      const update = updateType.fromBuffer(Buffer.from(evt.data));
      bufferToImage(update.previewImage.bytes).then((img) =>
        document.getElementById("preview").replaceChildren(img),
      );
      document.getElementById("state").innerText = `State: ${update.state}`;
      document.getElementById(
        "space",
      ).innerText = `Space remaining: ${update.spaceRemaining} GiB`;
    };

    ws.onclose = function () {
      alert("Connection is closed...");
    };
  } else {
    alert("WebSocket NOT supported by your Browser!");
  }
}

window.start = start;
