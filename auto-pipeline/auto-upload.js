import { chromium } from "playwright";
import dotenv from "dotenv";
import fs from "fs-extra";
import OpenAI from "openai";
import path from "path";

dotenv.config();

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const INPUT_DIR = "./input";
const UPLOADED_DIR = "./uploaded";

async function generateMetadata() {
  const prompt = `Generate JSON only. No explanation. No markdown.
{
  "title": "lo-fi song title in English",
  "spotify_description": "short description for Spotify (max 200 chars)",
  "youtube_description": "YouTube description with mood and use case (max 500 chars)",
  "tags": ["tag1","tag2",...20 tags total]
}
Theme: midnight, rain, Tokyo, study, chill, cafe, warm lighting`;

  const response = await openai.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: prompt }],
    temperature: 0.9,
    response_format: { type: "json_object" },
  });

  return JSON.parse(response.choices[0].message.content);
}

async function uploadToDistroKid(metadata) {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log("Logging into DistroKid...");
  await page.goto("https://distrokid.com/signin/");
  await page.fill('input[type="email"]', process.env.DISTRO_EMAIL);
  await page.fill('input[type="password"]', process.env.DISTRO_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(5000);

  console.log("Opening upload page...");
  await page.goto("https://distrokid.com/new/");
  await page.waitForTimeout(5000);

  // TITLE
  await page.fill('input[name="title"]', metadata.title).catch(() => {
    console.log("Title field not found, trying alternative selector...");
  });

  // ARTIST
  const artistInput = page.locator('input[placeholder*="artist" i], input[name="artist"]').first();
  await artistInput.fill("lifeassetpartners").catch(() => {});

  // GENRE - Electronic
  await page.selectOption('select[name="genre"]', { label: "Electronic" }).catch(async () => {
    await page.selectOption('select[name="genre"]', { index: 1 }).catch(() => {});
  });

  // LANGUAGE - English
  await page.selectOption('select[name="language"]', { label: "English" }).catch(() => {});

  // INSTRUMENTAL
  const instrumentalRadio = page.locator('input[type="radio"]').filter({ hasText: /instru/i });
  await instrumentalRadio.check().catch(() => {});

  // AI GENERATED - YES
  const aiYes = page.locator('text=はい').nth(0);
  await aiYes.click().catch(() => {});

  // AUDIO UPLOAD
  const songFiles = await fs.readdir(INPUT_DIR);
  const songFile = songFiles.find(f => /\.(wav|mp3|m4a|flac|aiff)$/i.test(f));
  if (songFile) {
    const songPath = path.join(INPUT_DIR, songFile);
    await page.setInputFiles('input[type="file"][accept*="audio"], input[type="file"]:not([accept*="image"])', songPath)
      .catch(() => console.log("Audio upload selector not found"));
    console.log("Uploading audio:", songFile);
    await page.waitForTimeout(5000);
  } else {
    console.log("⚠️  No audio file found in ./input/");
  }

  // COVER UPLOAD
  const coverFile = songFiles.find(f => /\.(jpg|jpeg|png)$/i.test(f));
  if (coverFile) {
    const coverPath = path.join(INPUT_DIR, coverFile);
    await page.setInputFiles('input[type="file"][accept*="image"]', coverPath)
      .catch(() => console.log("Cover upload selector not found"));
    console.log("Uploading cover:", coverFile);
    await page.waitForTimeout(5000);
  } else {
    console.log("⚠️  No cover image found in ./input/");
  }

  // SAVE METADATA JSON
  await fs.writeJson(`./${metadata.title}.json`, metadata, { spaces: 2 });

  console.log("\n=====================");
  console.log("UPLOAD READY — confirm in browser");
  console.log("=====================");
  console.log("TITLE:", metadata.title);
  console.log("\nYOUTUBE DESCRIPTION:");
  console.log(metadata.youtube_description);
  console.log("\nTAGS:");
  console.log(metadata.tags.join(", "));

  // MOVE FILES TO UPLOADED
  await fs.ensureDir(UPLOADED_DIR);
  if (songFile) {
    await fs.move(
      path.join(INPUT_DIR, songFile),
      path.join(UPLOADED_DIR, `${metadata.title}${path.extname(songFile)}`),
      { overwrite: true }
    );
  }
  if (coverFile) {
    await fs.move(
      path.join(INPUT_DIR, coverFile),
      path.join(UPLOADED_DIR, `${metadata.title}${path.extname(coverFile)}`),
      { overwrite: true }
    );
  }
  console.log("\nFiles archived to ./uploaded/");
  console.log("Browser stays open — submit manually when ready.");
}

async function main() {
  console.log("=====================");
  console.log("AI MUSIC PIPELINE");
  console.log("=====================");

  const metadata = await generateMetadata();
  console.log("\nGenerated metadata:");
  console.log(JSON.stringify(metadata, null, 2));

  await uploadToDistroKid(metadata);
}

main().catch(console.error);
