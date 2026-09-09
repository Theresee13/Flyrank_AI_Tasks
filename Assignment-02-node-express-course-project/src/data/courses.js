const courses = [];
let nextCourseId = 1;

function listCourses() {
  return courses;
}

function findCourse(id) {
  return courses.find((course) => course.id === id);
}

function createCourse(course) {
  const newCourse = { id: nextCourseId, ...course };
  nextCourseId += 1;
  courses.push(newCourse);
  return newCourse;
}

function updateCourse(id, course) {
  const existingCourse = findCourse(id);
  if (!existingCourse) return null;

  Object.assign(existingCourse, course);
  return existingCourse;
}

function deleteCourse(id) {
  const courseIndex = courses.findIndex((course) => course.id === id);
  if (courseIndex === -1) return false;

  courses.splice(courseIndex, 1);
  return true;
}

module.exports = { createCourse, deleteCourse, findCourse, listCourses, updateCourse };
