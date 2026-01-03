// ===============================
// AUTH MODULE
// ===============================

function saveToken(token) {
    localStorage.setItem("token", token);
}

function getToken() {
    return localStorage.getItem("token");
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/login";
}

async function login(email, password) {
    return await apiRequest("/login", "POST", { email, password });
}

async function registerUser(data) {
    return await apiRequest("/register", "POST", data);
}

function isLoggedIn() {
    return localStorage.getItem("token") !== null;
}

// Auto-redirect if user not logged in (for protected pages)
function protectRoute() {
    if (!isLoggedIn()) {
        window.location.href = "/login";
    }
}
