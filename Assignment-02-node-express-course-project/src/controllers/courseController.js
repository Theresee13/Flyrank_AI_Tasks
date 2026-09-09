const courseStore = require("../data/courses");

function validateCourse(payload) {
  const { title, instructor, duration } = payload;
  if (typeof title !== "string" || title.trim() === "") {
    return "title is required";
  }
  if (typeof instructor !== "string" || instructor.trim() === "") {
    return "instructor is required";
  }
  if (typeof duration !== "number" || !Number.isFinite(duration) || duration <= 0) {
    return "duration must be a positive number";
  }
  return null;
}

function parseCourseId(value) {
  const id = Number(value);
  return Number.isInteger(id) && id > 0 ? id : null;
}

function listCourses(_request, response) {
  response.json(courseStore.listCourses());
}

function getCourse(request, response) {
  const id = parseCourseId(request.params.id);
  const course = id && courseStore.findCourse(id);
  if (!course) return response.status(404).json({ error: "Course not found" });
  return response.json(course);
}

function createCourse(request, response) {
  const validationError = validateCourse(request.body);
  if (validationError) return response.status(400).json({ error: validationError });

  const course = courseStore.createCourse({
    title: request.body.title.trim(),
    instructor: request.body.instructor.trim(),
    duration: request.body.duration,
  });
  return response.status(201).json(course);
}

function replaceCourse(request, response) {
  const id = parseCourseId(request.params.id);
  if (!id || !courseStore.findCourse(id)) {
    return response.status(404).json({ error: "Course not found" });
  }

  const validationError = validateCourse(request.body);
  if (validationError) return response.status(400).json({ error: validationError });

  const course = courseStore.updateCourse(id, {
    title: request.body.title.trim(),
    instructor: request.body.instructor.trim(),
    duration: request.body.duration,
  });
  return response.json(course);
}

function removeCourse(request, response) {
  const id = parseCourseId(request.params.id);
  if (!id || !courseStore.deleteCourse(id)) {
    return response.status(404).json({ error: "Course not found" });
  }
  return response.status(204).send();
}

module.exports = { createCourse, getCourse, listCourses, removeCourse, replaceCourse };
