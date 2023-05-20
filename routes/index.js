require("dotenv").config();
const express = require("express");
const router = express.Router();
const scraper = require("../resources/js/scraper.js");
const runner = require("../resources/js/example_runner");
const fs = require("fs");
const child_process = require("child_process");

router.get("/", function (req, res, next) {
  res.render("index");
});

router.post("/predict", async function (req, res, next) {
  const url = req.body.url;
  if (!url) {
    return res.status(400).send({ error: "No URL provided" });
  }

  // Save the URL to a JSON file
  fs.writeFileSync(process.env.LINKS_JSON_PATH, JSON.stringify([url]), "utf8");

  // Run the scraper
  await scraper.main();

  // Run the python script
  const output = await child_process.spawnSync("python", [
    process.env.PYTHON_SCRIPT_PATH,
  ]);

  const prediction = await child_process.spawnSync(".venv/Scripts/python.exe", [
    "-c",
    `import sys; sys.path.insert(0, '${process.env.PYTHON_WEB_SCRIPT_PATH}'); import web_script; print(web_script.main('${process.env.CSV_FILE_PATH}'))`,
  ]);

  if (prediction.status === 0) {
    let output = prediction.stdout.toString().trim();
    // [179691.86598665826, 175380.04435448247] <- needs to be parsed:
    output = prediction.stdout.toString().trim().slice(1, -1).split(", ");
    output = output.map((x) => parseFloat(x));
    output = output.map((x) => Math.round(x));
    output.sort((a, b) => a - b);

    res.status(200).send({
      message: "The price range is: " + output[0] + " - " + output[1] + " EUR",
    });
    console.log(output);
  } else {
    console.error(
      "An error occurred while executing the Python script. Error message:"
    );
    console.error(prediction.stderr.toString());
    res.status(500).send({
      error: "Server error. Please try again later.",
    });
  }
});

module.exports = router;
