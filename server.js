const express = require("express");
require("dotenv").config();

const app = express();

// Middleware
app.use(express.json());

// Health check route
app.get("/", (req, res) => {
  res.send("API is running...");
});

// Example route test
app.get("/health", (req, res) => {
  res.status(200).json({ status: "OK" });
});

// PORT from environment (Render injects this)
const PORT = process.env.PORT || 5000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
