const inputField = document.getElementById("inputField");
const submitBtn = document.getElementById("submitBtn");
const outputMsg = document.getElementById("outputMsg");

// List of phrases as regex patterns
const regexes = [/a+y+o+/i, /h+o+m+i+e+/i, /s+k+i+l+l+e+t+s+/i];

submitBtn.addEventListener("click", () => {
  const input = inputField.value.replace(/0/g, "o").replace(/1/g, "i");

  let found = false;
  for (let regex of regexes) {
    if (regex.test(input)) {
      found = true;
      break;
    }
  }

  if (found) {
    inputField.style.backgroundColor = "#ffcccc"; // light red
    outputMsg.textContent = "Hey! Found some issues!";
  } else {
    inputField.style.backgroundColor = "#ccffcc"; // light green
    outputMsg.textContent = "All clear!";
  }
});
