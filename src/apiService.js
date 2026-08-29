const API_BASE = import.meta.env.VITE_BASE_URL || 'http://localhost:8000';
const JWT_TOKEN = import.meta.env.VITE_JWT_TOKEN || '';
import MarkdownIt from "markdown-it";
const md = new MarkdownIt();



export const hasRagAPI = !!import.meta.env.VITE_BASE_URL;


/**
 * Loads temples from the RAG model API.
 * Expected output: [{ name: "string", lat: "int", long: "int" }]
 */
export const loadTemplesAPI = async () => {
    try {
        const res = await fetch(`${API_BASE}/api/v1/load_temples/`, {
            method: 'POST'
        });
        if (!res.ok) throw new Error('Network response was not ok');
        return await res.json();
    } catch (error) {
        console.error("Error loading temples from API:", error);
        return null;
    }
};

/**
 * Fetches specific temple data (description).
 * Expected output: { name: "string", desc: "string" }
 */
export const fetchTempleDataAPI = async (templeName) => {
    try {
        const res = await fetch(`${API_BASE}/api/v1/temple_data/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: templeName })
        });
        if (!res.ok) throw new Error('Network response was not ok');
        return await res.json();
    } catch (error) {
        console.error("Error fetching temple data from API:", error);
        return null;
    }
};

/**
 * Asks the RAG model a query.
 * Expected input: { header: "Bearer <JWT Token>", body: { query: "string" } }
 * Expected output: { success: "bool", message: "string" }
 */
export const askRagModelAPI = async (query, uuid) => {
    try {
        const headers = { 'Content-Type': 'application/json' };
        if (JWT_TOKEN) {
            headers['Authorization'] = `Bearer ${JWT_TOKEN}`;
        }

        const res = await fetch(`${API_BASE}/api/v1/ask/`, {
            method: 'POST',
            headers,
            body: JSON.stringify({ query, uuid })
        });
        if (!res.ok) throw new Error('Network response was not ok');
        let temp = await res.json()
        temp["message"] = md.render(temp["message"])
        return temp;
    } catch (error) {
        console.error("Error asking RAG model:", error);
        return null;
    }
};

/**
 * Connects to the backend to generate a new session UUID.
 * Expected output: { uuid: "string" }
 */
export const connectAuthAPI = async () => {
    try {
        const headers = { 'Content-Type': 'application/json' };
        if (JWT_TOKEN) {
            headers['Authorization'] = `Bearer ${JWT_TOKEN}`;
        }

        const res = await fetch(`${API_BASE}/auth/v1/connect`, {
            method: 'POST',
            headers,
            body: JSON.stringify({})
        });
        if (!res.ok) throw new Error('Network response was not ok');
        return await res.json();
    } catch (error) {
        console.error("Error connecting to auth API:", error);
        return null;
    }
};
