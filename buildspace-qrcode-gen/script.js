function changeBackgroundColor(color) {
  document.body.style.backgroundColor = color;
  const outputContainer = document.getElementById("outputContainer");
  outputContainer.style.backgroundColor = color;
}

function generateQRCode() {
  const titleInput = document.getElementById("titleInput").value;
  const descriptionInput = document.getElementById("descriptionInput").value;
  const linkInput = document.getElementById("linkInput").value;

  const textContainer = document.getElementById("textContainer");
  textContainer.innerHTML =
    "<h2>" + titleInput + "</h2>" + "<p>" + descriptionInput + "</p>";

  const qrCodeContainer = document.getElementById("qrCodeContainer");
  qrCodeContainer.innerHTML = "";

  const qrText = linkInput;

  const qr = new QRCode(qrCodeContainer, {
    text: qrText,
    width: 200,
    height: 200,
  });

  const outputContainer = document.getElementById("outputContainer");
  outputContainer.classList.remove("hide-container");
  outputContainer.classList.add("show-container");

  setTimeout(() => {
    html2canvas(outputContainer).then(function (canvas) {
      const url = canvas.toDataURL("image/png");
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "output.png";
      anchor.click();
    });
  }, 100);
}
