let authHeaders = {};

document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    authHeaders = {
        "Authorization": "Basic " + btoa(username + ":" + password)
    };

    let response = await fetch("/", { method: "GET", headers: authHeaders });

    if (response.ok) {
        document.getElementById("login-message").innerHTML = `<p style="color:green;">✅ Inicio de sesión exitoso</p>`;
        document.getElementById("loginForm").style.display = "none";
        document.getElementById("main-content").style.display = "block";
    } else {
        document.getElementById("login-message").innerHTML = `<p style="color:red;">❌ Usuario o contraseña incorrectos</p>`;
    }
});

document.getElementById("insertForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    let formData = new FormData(this);
    formData.append("sheet_name", document.getElementById("sheet").value);

    let response = await fetch("/insert_project/", {
        method: "POST",
        body: formData,
        headers: authHeaders
    });

    let result = await response.json();
    let messageDiv = document.getElementById("response-message");

    if (result.message) {
        messageDiv.innerHTML = `<p style="color:green;">${result.message}</p>`;
    } else {
        messageDiv.innerHTML = `<p style="color:red;">Error: ${result.error}</p>`;
    }
});
