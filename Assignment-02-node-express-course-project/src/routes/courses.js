const express = require("express");
const controller = require("../controllers/courseController");

const router = express.Router();

router.route("/").get(controller.listCourses).post(controller.createCourse);
router.route("/:id").get(controller.getCourse).put(controller.replaceCourse).delete(controller.removeCourse);

module.exports = router;
