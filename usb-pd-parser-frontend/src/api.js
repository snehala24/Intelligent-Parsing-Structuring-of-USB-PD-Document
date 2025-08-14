import axios from "axios";

// Change this to your backend's URL
const API_BASE = "http://localhost:8000";

export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return axios.post(`${API_BASE}/upload`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (progressEvent) => {
      const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      console.log(`Upload Progress: ${percent}%`);
    },
  });
};

export const getResults = async () => {
  return axios.get(`${API_BASE}/results`);
};
