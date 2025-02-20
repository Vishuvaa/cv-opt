const chat = document.getElementById("chatInput");
const submit = document.getElementById("submitButton");
const record = document.getElementById("recordButton");
const historyArea = document.getElementById("chatArea");

document.addEventListener("DOMContentLoaded", function () {
  const ws = new WebSocket("ws://127.0.0.1:8000/ws");
  let accumulatedData = ""; // Variable to accumulate streamed data

  ws.onopen = () => {
    console.log("WebSocket connection opened.");
  };

  ws.onmessage = (event) => {
    let data = event.data;

    // Append the new data to the accumulated data
    accumulatedData += data;

    // Format the incoming data to handle '**' as subheadings and bold text
    let formattedData = formatMarkdownToHtml(accumulatedData);

    // Update the #report div with the formatted data
    document.getElementById("report").innerHTML = formattedData;
  };

  ws.onerror = (error) => {
    console.error("WebSocket error:", error);
  };

  ws.onclose = () => {
    console.log("WebSocket connection closed.");
  };

  // Close WebSocket when the user leaves the page
  window.addEventListener("beforeunload", () => {
    ws.close();
  });

  // Function to format markdown-like content into HTML
  function formatMarkdownToHtml(text) {
    // Updated regex to match '**text**' while ignoring numbers with a dot (e.g., '1.') preceding the text
    let formattedText = text.replace(
      /(?:\d+\.\s*)?\*\*(.*?)\*\*/g,
      (match, p1) => {
        // Wrap the text inside <h4> and <strong>
        return `<h4><strong>${p1}</strong></h4>`;
      }
    );

    return formattedText;
  }
});

function putUserText(userText) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("chat-answer");

  const messageContent = document.createElement("p");
  messageContent.textContent = userText;

  messageDiv.appendChild(messageContent);
  historyArea.appendChild(messageDiv);
  historyArea.scrollTop = historyArea.scrollHeight;
}

function putBotText(botText) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("bot-answer");

  const messageContent = document.createElement("p");
  messageContent.textContent = botText;

  messageDiv.appendChild(messageContent);

  historyArea.appendChild(messageDiv);
  historyArea.scrollTop = historyArea.scrollHeight;
}

function renderCV(cvData) {
  let content = "";
  historyArea.style.padding = "15px";

  if (cvData.name) content += `<div class="name">${cvData.name}</div>`;

  if (cvData.email || cvData.phone || cvData.location) {
    content += `<div class="contact-info">`;
    if (cvData.email)
      content += `<p><strong>Email:</strong> ${cvData.email}</p>`;
    if (cvData.phone)
      content += `<p><strong>Phone:</strong> ${cvData.phone}</p>`;
    if (cvData.location)
      content += `<p><strong>Location:</strong> ${cvData.location}</p>`;
    content += `</div>`;
  }

  if (cvData.education && cvData.education.length > 0) {
    content += `<p class="section-title">Education:</p><ul>`;
    cvData.education.forEach((edu) => {
      content += `<li><strong>${edu.degree} at ${edu.institute} (${edu.year.month} ${edu.year.year})</strong></li>`;
    });
    content += `</ul>`;
  }

  if (cvData.work_experience && cvData.work_experience.length > 0) {
    content += `<p class="section-title">Work Experience:</p><ul>`;
    cvData.work_experience.forEach((job) => {
      content += `<li><strong>${job.role}</strong> at ${job.company} (${job.start_date} - ${job.end_date})<br><br>${job.description}</li>`;
    });
    content += `</ul>`;
  }

  if (cvData.skills && cvData.skills.length > 0) {
    content += `<p class="section-title">Skills:</p><p class = "skills">${cvData.skills.join(
      ", "
    )}</p>`;
  }

  if (cvData.projects && cvData.projects.length > 0) {
    content += `<p class="section-title">Projects:</p><ul>`;
    cvData.projects.forEach((project) => {
      content += `<li><strong>${project.name}:</strong><br><br>${project.description}</li>`;
    });
    content += `</ul>`;
  }

  if (cvData.courses && cvData.courses.length > 0) {
    content += `<p class="section-title">Courses:</p><ul>`;
    cvData.courses.forEach((course) => {
      content += `<li>${course.name}: ${course.description}</li>`;
    });
    content += `</ul>`;
  }

  if (cvData.certifications && cvData.certifications.length > 0) {
    content += `<p class="section-title">Certifications:</p><ul>`;
    cvData.certifications.forEach((cert) => {
      content += `<li>${cert.name}: ${cert.description}</li>`;
    });
    content += `</ul>`;
  }

  historyArea.innerHTML = content;
}

async function generateCV(e) {
  e.preventDefault();
  historyArea.innerHTML = "";
  const id = "1234";
  let genButton = document.getElementById("generateButton");

  genButton.innerText = "Generating your CV...";
  fetch("http://127.0.0.1:8000/generateCV", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: id }), // Send the input data as JSON
  })
    .then((response) => response.json())
    .then((data) => {
      let genButton = document.getElementById("generateButton");
      genButton.remove();
      renderCV(data.cv);
      console.log("Response from backend:", data);
    });
}

function sendData(data) {
  fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text: data }), // Send the input data as JSON
  })
    .then((response) => response.json())
    .then((data) => {
      putBotText(data.message);
      console.log("Response from backend:", data);
      if (data.message.trim() == "Thank you for your responses.") {
        chat.remove();
        submit.remove();
        record.remove();
        const generate = document.createElement("button");
        generate.id = "generateButton";
        generate.textContent = "Generate CV";
        document.getElementById("chatAreaBottom").appendChild(generate);

        generate.addEventListener("click", (e) => generateCV(e));
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

submit.addEventListener("click", (e) => {
  e.preventDefault();
  userText = chat.value;
  chat.value = "";
  chat.setAttribute("placeholder", "");
  putUserText(userText);
  sendData(userText);
});

if (navigator.mediaDevices.getUserMedia()) {
  function setupSuccess(stream) {
    console.log("setup success");
    mediarecorder = new MediaRecorder(stream);

    record.addEventListener("click", (e) => {
      e.preventDefault();
      if (mediarecorder.state == "recording") {
        mediarecorder.stop();
        if (icon.classList.contains("fa-circle-xmark")) {
          record.style.backgroundColor = "rgb(49, 49, 50)";
          icon.classList.remove("fa-circle-xmark");
          icon.classList.add("fa-solid", "fa-microphone");
        }
        record.style.backgroundColor = "rgb(49, 49, 50)";
      } else {
        mediarecorder.start();
        chat.style.color = "rgb(176, 171, 171)";
        chat.value = "Recording in progress..";
        if (icon.classList.contains("fa-microphone")) {
          record.style.backgroundColor = "rgb(236, 75, 75)";
          icon.classList.remove("fa-microphone");
          icon.classList.add("fa-solid", "fa-circle-xmark");
        }
        record.style.backgroundColor = "rgb(236, 75, 75)";
      }

      let chunks = [];
      mediarecorder.ondataavailable = (e) => {
        chunks.push(e.data);
      };

      mediarecorder.onstop = () => {
        chat.style.color = "rgb(176, 171, 171)";
        chat.value = "Transcribing your voice";

        const blob = new Blob(chunks, { type: "audio/webm" });
        chunks = []; // resetting chunks on stop

        const formData = new FormData();
        formData.append("audio", blob);

        fetch("http://127.0.0.1:8000/transcribe", {
          method: "POST",
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            chat.style.color = "rgb(0, 0, 0)";
            chat.value = data.transcript;
          });
      };
    });
  }

  function setupFailure(err) {
    console.log("setup failure");
  }

  navigator.mediaDevices
    .getUserMedia({ audio: true })
    .then(setupSuccess)
    .catch(setupFailure);
} else alert("Your browzer dont support audio recording");
