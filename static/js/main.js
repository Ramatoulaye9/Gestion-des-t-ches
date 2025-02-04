// static/js/main.js
const API_URL = "http://127.0.0.1:5000";
let token = "";


// Fonction d'inscription
function inscription() {
  const username = document.getElementById("register-username").value;
  const password = document.getElementById("register-password").value;
  fetch(`${API_URL}/inscription`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message);
    })
    .catch((error) => console.error("Erreur:", error));
}

// Fonction de connexion
function login() {
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;
  fetch(`${API_URL}/connexion`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  })
    .then((response) => response.json())
    .then((data) => {
        if (data.token) {
          localStorage.setItem("token", data.token);
          token = data.token; // Ajoute cette ligne
          localStorage.setItem("username", username); // Sauvegarde aussi l'username
          document.getElementById("auth").style.display = "none";
          document.getElementById("tasks").style.display = "block";
          document.getElementById("username-display").textContent = `Bienvenue, ${username} !`;
          fetchTasks();
        } else {
          alert(data.message || "Erreur lors de la connexion");
        }
      })
    .catch((error) => console.error("Erreur:", error));
}

// Récupérer les tâches
function fetchTasks() {
    if (!token) {
      console.error("Token non disponible. Impossible de récupérer les tâches.");
      return;
    }
  
    fetch(`${API_URL}/taches`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => response.json())
      .then((tasks) => {
        const tasksList = document.getElementById("tasks-list");
        tasksList.innerHTML = "";
        tasks.forEach((task) => {
          tasksList.innerHTML += `
            <li class="task">
              <span>${task.title} - ${task.status} - ${task.due_date || "Pas de date"}</span>
              <select onchange="updateTask(${task.id}, this.value)">
                <option value="En cours" ${task.status === "En cours" ? "selected" : ""}>En cours</option>
                <option value="Suspendu" ${task.status === "Suspendu" ? "selected" : ""}>Suspendu</option>
                <option value="Terminé" ${task.status === "Terminé" ? "selected" : ""}>Terminé</option>
              </select>
              <button onclick="updateTask(${task.id}, this.value)">Modifier</button>
              <button onclick="deleteTask(${task.id})">Supprimer</button>
            </li>
          `;
        });
      })
      .catch((error) => console.error("Erreur:", error));
  }
  
// Ajouter une tâche
function addTask() {
    if (!token) {
      alert("Veuillez vous connecter pour ajouter une tâche.");
      return;
    }
  
    const title = document.getElementById("task-title").value.trim();
    const dueDate = document.getElementById("task-date").value;
    const status = document.getElementById("task-status").value;
  
    if (!title) {
      alert("Veuillez entrer un titre pour la tâche.");
      return;
    }
  
    fetch(`${API_URL}/taches`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ title, due_date: dueDate, status }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          document.getElementById("task-title").value = "";
          fetchTasks();
        } else {
          alert("Erreur lors de l'ajout de la tâche");
        }
      })
      .catch((error) => console.error("Erreur:", error));
  }  

function updateTask(taskId, newStatus) {
  fetch(`${API_URL}/taches/${taskId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ status: newStatus }),
  })
    .then((response) => response.json())
    .then((data) => {
      alert(data.message);
      fetchTasks(); // Recharger les tâches après la mise à jour
    })
    .catch((error) => console.error("Erreur:", error));
}

function deleteTask(id) {
  fetch(`${API_URL}/taches/${id}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
  })
    .then((response) => response.json())
    .then(() => fetchTasks()) // Recharger les tâches après la suppression
    .catch((error) => console.error("Erreur:", error));
}

window.onload = function () {
    token = localStorage.getItem("token"); // Assigne le token globalement
    const username = localStorage.getItem("username");
    
    if (token) {
      document.getElementById("tasks").style.display = "block";
      document.getElementById("auth").style.display = "none";
      document.getElementById("username-display").textContent = `Bienvenue, ${username || "Utilisateur"} !`;
      fetchTasks();
    } else {
      document.getElementById("tasks").style.display = "none";
      document.getElementById("auth").style.display = "flex";
    }
  };  
  

// Déconnexion : réinitialise le token et affiche les formulaires d'authentification
function logout() {
  localStorage.removeItem("token");
  document.getElementById("auth").style.display = "flex";
  document.getElementById("tasks").style.display = "none";
  document.getElementById("username").textContent = "Veuillez vous connecter";
}
