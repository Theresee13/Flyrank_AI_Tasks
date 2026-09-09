# Assignment 02: Node.js Course Management API

An Express REST API for managing courses with in-memory data, request validation, and Docker support.

## Run locally

```bash
cd Assignment-02-node-express-course-project
npm install
npm start
```

The service runs at `http://localhost:3000`.

## Run with Docker

```bash
docker compose up --build
```

## Endpoints

| Method | Endpoint | Description | Success code |
| --- | --- | --- | --- |
| GET | `/health` | Service health check | 200 |
| POST | `/courses` | Create a course | 201 |
| GET | `/courses` | List courses | 200 |
| GET | `/courses/:id` | Fetch a course | 200 |
| PUT | `/courses/:id` | Fully replace a course | 200 |
| DELETE | `/courses/:id` | Delete a course | 204 |

Create and update requests require `title`, `instructor`, and a positive numeric `duration`.

```json
{
  "title": "REST API Design",
  "instructor": "Leosce",
  "duration": 6
}
```

Unknown course IDs return `404`; invalid request bodies return `400`.
