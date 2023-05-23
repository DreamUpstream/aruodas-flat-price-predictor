const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const fs = require("fs");

puppeteer.use(StealthPlugin());

const directory = "resources/file_storage/downloaded_htmls";

const launchOptions = {
  headless: true,
  defaultViewport: {
    width: 1280,
    height: 800,
  },
  args: ["--no-sandbox"],
  userAgent:
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
};

let index = 0;

async function downloadHTML(url, directory) {
  const browser = await puppeteer.launch(launchOptions);
  const page = await browser.newPage();

  await page.goto(url);

  const content = await page.content();
  await browser.close();

  const filename = `${directory}/listing.html`;
  fs.writeFile(filename, content, "utf8", (err) => {
    if (err) throw err;
    console.log("The file has been saved!");
  });
}

async function main() {
  const links = await fs.readFileSync(
    "resources/file_storage/links/links.json",
    "utf8"
  );
  const linksArray = JSON.parse(links);
  console.log("linksarr: ", linksArray);

  for (let i = 0; i < linksArray.length; i++) {
    await downloadHTML(linksArray[i], directory);
  }
}

module.exports.main = main;
