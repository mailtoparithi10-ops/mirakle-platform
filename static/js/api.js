// ===============================
// API HELPER MODULE
// ===============================

const API_BASE_URL = "/api";

async function apiRequest(endpoint, method = "GET", data = null, auth = false) {
    const options = {
        method,
        headers: {
            "Content-Type": "application/json"
        }
    };

    if (auth) {
        const token = localStorage.getItem("token");
        if (token) options.headers["Authorization"] = `Bearer ${token}`;
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error("🔥 API ERROR:", error);
        return { error: true };
    }
}
