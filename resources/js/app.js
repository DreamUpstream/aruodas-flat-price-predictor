async function saveListing() {
  const url = document.getElementById("url").value;
  const messageDiv = document.getElementById("message");

  // Display loading spinner
  messageDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

  // Send the link to the server
  const response = await fetch("/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ url: url }),
  });

  const result = await response.json();

  // Display the server's response
  if (response.ok) {
    messageDiv.innerHTML = '<i class="fas fa-check"></i> ' + result.message;
  } else {
    messageDiv.innerHTML = '<i class="fas fa-times"></i> ' + result.error;
  }
}

// #save_button click listener:
document.getElementById("save_button").addEventListener("click", saveListing);
