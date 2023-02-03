const video = document.getElementById("videoElement");
const statusText = document.getElementById("status");

if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(function (stream) {
      video.srcObject = stream;
      statusText.innerText = "Your webcam is connected :)";
      statusText.classList.add("success");
    })
    .catch(function (err) {
      console.log("Something went wrong!");
      statusText.innerText =
        "Your webcam hasn't connected :( Please check the browser permissions";
      statusText.classList.add("failure");
    });
}

const getFrame = () => {
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const data = canvas.toDataURL("image/jpeg");
  return data;
};

const scroll = (direction) => {
  if (direction === "0") {
    scrollTo({
      top: globalThis.window.scrollY + 100,
      left: 0,
      behavior: "smooth",
    });
  } else if (direction === "1") {
    scrollTo({
      top: globalThis.window.scrollY - 100,
      left: 0,
      behavior: "smooth",
    });
  } else {
  }
};

// const WS_URL = "ws://localhost:8086/get_gesture";
const WS_URL =
  "wss://test-deployment-production-a012.up.railway.app/get_gesture";
const FPS = 3;
const ws = new WebSocket(WS_URL);
ws.onopen = () => {
  console.log(`Connected to ${WS_URL}`);
  setInterval(() => {
    ws.send(getFrame());
  }, 1000 / FPS);
};

ws.onmessage = (msg) => {
  let rec = JSON.parse(msg.data)["gesture"];
  console.log(rec);
  console.log(rec.type);
  scroll(rec);
};
