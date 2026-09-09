// Application entry point: keep startup separate from route definitions so
// the exported Express instance remains straightforward to test.
const express = require("express");
const courseRoutes = require("./routes/courses");

const app = express();
const port = Number(process.env.PORT) || 3000;

app.use(express.json());

app.get("/health", (_request, response) => response.json({ status: "ok" }));
app.use("/courses", courseRoutes);
app.use((_request, response) => response.status(404).json({ error: "Route not found" }));

if (require.main === module) {
  app.listen(port, () => console.log(`Course API listening on port ${port}`));
}

module.exports = app;
