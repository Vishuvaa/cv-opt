document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("questionForm");
  const button = document.getElementById("submit");

  form.addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent default form submission
    const jd = document.getElementById("jd").value.trim();
    const cvFile = document.getElementById("cv").files[0];

    // Validate required fields
    if (!jd || !cvFile) {
      alert("Please fill in all required fields.");
      return;
    }

    button.innerText = "Processing your input..";
    const formData = new FormData();
    formData.append("jd", jd);
    formData.append("cv", cvFile);

    try {
      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      button.innerText = "Analyze ✨";
      const result = await response.json();
      window.location.href = "http://127.0.0.1:8000/analyze";

      // redirect
    } catch (error) {
      console.error("Submission error:", error);
      alert("Failed to submit the form. Please try again.");
    }
  });
});
