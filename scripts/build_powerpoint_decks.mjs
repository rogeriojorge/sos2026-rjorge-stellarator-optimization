#!/usr/bin/env node

import fs from "node:fs/promises";
import fsSync from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SPEC_PATH = path.join(ROOT, "slides", "powerpoint", "deck_spec.json");
const PPTX_DIR = path.join(ROOT, "slides", "pptx");
const PREVIEW_ROOT = path.join(ROOT, "data", "generated", "pptx_previews");
const LAYOUT_ROOT = path.join(ROOT, "data", "generated", "pptx_layouts");
const MANIFEST_PATH = path.join(ROOT, "data", "generated", "status", "powerpoint_decks.json");
const UW_CREST_WHITE = path.join(ROOT, "assets", "logos", "uw_crest_white.png");
const UW_CREST_RED = path.join(ROOT, "assets", "logos", "uw_crest_red.png");
const SLIDE_SIZE = { width: 1280, height: 720 };
const REPO_URL = "github.com/rogeriojorge/sos2026-rjorge-stellarator-optimization";
const DOCS_URL = "sos2026-rjorge-stellarator-optimization.readthedocs.io";

const transparent = "#00000000";
const palette = {
  paper: "#fefefe",
  paperWarm: "#fefefe",
  ink: "#2b2b2b",
  muted: "#6f6f6f",
  faint: "#dddddd",
  panel: "#ffffff",
  uwRed: "#c5050c",
  uwDarkRed: "#9b0000",
  uwGray: "#646569",
  lightGray: "#f4f4f4",
  navy: "#1f2937",
  teal: "#047a7a",
  blue: "#2563eb",
  green: "#15803d",
  amber: "#c46a00",
  coral: "#c5050c",
  violet: "#5b2c6f",
  slate: "#444444",
};

const deckThemes = {
  lecture_1_geometry_metrics: {
    accent: palette.uwRed,
    accent2: palette.uwGray,
    dark: palette.uwRed,
    tag: "Lecture 1",
    loopFocus: ["equilibrium", "Boozer spectrum", "metrics"],
  },
  lecture_2_coils_single_stage: {
    accent: palette.uwRed,
    accent2: palette.uwGray,
    dark: palette.uwRed,
    tag: "Lecture 2",
    loopFocus: ["coils", "B dot n", "single stage"],
  },
  lecture_3_transport_turbulence_metrics: {
    accent: palette.uwRed,
    accent2: palette.uwGray,
    dark: palette.uwRed,
    tag: "Lecture 3",
    loopFocus: ["neoclassical", "turbulence", "validation"],
  },
  lecture_4_integrated_workflow: {
    accent: palette.uwRed,
    accent2: palette.uwGray,
    dark: palette.uwRed,
    tag: "Lecture 4",
    loopFocus: ["profiles", "Pareto", "decisions"],
  },
};

function usage() {
  return [
    "Usage: node scripts/build_powerpoint_decks.mjs [--deck <deck_id>] [--preview-scale <number>]",
    "",
    "Builds editable PPTX decks from slides/powerpoint/deck_spec.json using @oai/artifact-tool.",
    "Set ARTIFACT_TOOL_ENTRYPOINT if the bundled Codex runtime is not available.",
  ].join("\n");
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    if (!key.startsWith("--")) throw new Error(`Unexpected argument: ${key}`);
    const value = argv[i + 1];
    if (!value || value.startsWith("--")) {
      args[key.slice(2)] = true;
      continue;
    }
    args[key.slice(2)] = value;
    i += 1;
  }
  return args;
}

function artifactToolEntrypoint() {
  const home = process.env.HOME || process.cwd();
  const candidates = [
    process.env.ARTIFACT_TOOL_ENTRYPOINT,
    path.join(
      home,
      ".cache",
      "codex-runtimes",
      "codex-primary-runtime",
      "dependencies",
      "node",
      "node_modules",
      "@oai",
      "artifact-tool",
      "dist",
      "artifact_tool.mjs",
    ),
    path.join(
      home,
      ".cache",
      "codex-runtimes",
      "codex-primary-runtime",
      "dependencies",
      "node",
      "node_modules",
      "@oai",
      "artifact-tool",
      "dist",
      "node",
      "artifact_tool.mjs",
    ),
    path.join(ROOT, "node_modules", "@oai", "artifact-tool", "dist", "artifact_tool.mjs"),
    path.join(ROOT, "node_modules", "@oai", "artifact-tool", "dist", "node", "artifact_tool.mjs"),
  ].filter(Boolean);

  const found = candidates.find((candidate) => fsSync.existsSync(candidate));
  if (!found) {
    throw new Error(
      [
        "Could not find @oai/artifact-tool.",
        "Run inside the Codex desktop runtime or set ARTIFACT_TOOL_ENTRYPOINT=/path/to/artifact_tool.mjs.",
      ].join("\n"),
    );
  }
  return found;
}

async function importArtifactTool() {
  return import(pathToFileURL(artifactToolEntrypoint()).href);
}

function arrayBufferFromBuffer(buffer) {
  return buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength);
}

async function saveBlobToFile(blob, outputPath) {
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  if (blob && typeof blob.arrayBuffer === "function") {
    await fs.writeFile(outputPath, Buffer.from(await blob.arrayBuffer()));
    return;
  }
  if (blob instanceof Uint8Array || Buffer.isBuffer(blob)) {
    await fs.writeFile(outputPath, Buffer.from(blob));
    return;
  }
  throw new Error("Expected a Blob or Uint8Array from artifact-tool export.");
}

function line(fill = transparent, width = 0) {
  return { style: "solid", fill, width };
}

function rect(slide, x, y, w, h, fill = transparent, stroke = transparent, strokeWidth = 0) {
  return slide.shapes.add({
    geometry: "rect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: line(stroke, strokeWidth),
  });
}

function text(slide, value, x, y, w, h, options = {}) {
  const box = rect(slide, x, y, w, h, options.fill ?? transparent, options.stroke ?? transparent, options.strokeWidth ?? 0);
  box.text = String(value ?? "");
  box.text.fontSize = options.fontSize ?? 24;
  box.text.color = options.color ?? palette.ink;
  box.text.bold = Boolean(options.bold);
  box.text.typeface = options.typeface ?? (options.bold ? "Aptos Display" : "Aptos");
  box.text.alignment = options.align ?? "left";
  box.text.verticalAlignment = options.valign ?? "top";
  box.text.insets = options.insets ?? { left: 0, right: 0, top: 0, bottom: 0 };
  return box;
}

function titleFont(title) {
  if (title.length > 92) return 31;
  if (title.length > 72) return 35;
  return 42;
}

function bulletFont(value) {
  const len = String(value).length;
  if (len > 118) return 18;
  if (len > 88) return 20;
  if (len > 64) return 22;
  return 24;
}

function addPageTitle(slide, deck, item, slideNumber, total) {
  const theme = deckThemes[deck.id];
  addUwMark(slide);
  const titleWraps = item.title.length > 58;
  text(slide, item.title, 34, 42, 1008, titleWraps ? 92 : 70, {
    fontSize: titleFont(item.title),
    bold: true,
    color: palette.ink,
    valign: "middle",
  });
  rect(slide, 34, titleWraps ? 142 : 126, 92, 7, theme.accent);
  if (item.subtitle) {
    text(slide, item.subtitle, 148, titleWraps ? 138 : 122, 740, 26, {
      fontSize: 18,
      color: palette.muted,
      valign: "middle",
    });
  }
}

function addFooter(slide, deck, slideNumber) {
  rect(slide, 34, 660, 1120, 1, "#d0d0d0");
  text(slide, "SOS 2026 Stellarator Optimization, Rogerio Jorge, UW-Madison", 964, 675, 250, 18, {
    fontSize: 8,
    color: palette.muted,
    align: "right",
  });
  text(slide, "optimization workflow", 758, 675, 180, 18, {
    fontSize: 8,
    color: palette.muted,
    align: "right",
  });
  text(slide, DOCS_URL, 128, 675, 330, 18, {
    fontSize: 8,
    color: palette.muted,
    valign: "middle",
  });
  addSlideNumber(slide, slideNumber);
}

async function addImage(slide, relativePath, x, y, w, h, options = {}) {
  const absolutePath = path.join(ROOT, relativePath);
  if (!fsSync.existsSync(absolutePath)) {
    rect(slide, x, y, w, h, "#f3f4f6", "#d1d5db", 1);
    text(slide, `Missing image\n${relativePath}`, x + 20, y + 20, w - 40, h - 40, {
      fontSize: 18,
      color: palette.coral,
      valign: "middle",
      align: "center",
    });
    return;
  }
  const buffer = await fs.readFile(absolutePath);
  const image = slide.images.add({
    blob: arrayBufferFromBuffer(buffer),
    fit: options.fit ?? "contain",
    alt: options.alt ?? relativePath,
  });
  image.position = { left: x, top: y, width: w, height: h };
}

function addImageSync(slide, absolutePath, x, y, w, h, options = {}) {
  if (!fsSync.existsSync(absolutePath)) return undefined;
  const buffer = fsSync.readFileSync(absolutePath);
  const image = slide.images.add({
    blob: arrayBufferFromBuffer(buffer),
    fit: options.fit ?? "contain",
    alt: options.alt ?? path.basename(absolutePath),
  });
  image.position = { left: x, top: y, width: w, height: h };
  return image;
}

function addUwMark(slide, variant = "red-box") {
  if (variant === "red-box") {
    rect(slide, 1196, 0, 48, 82, palette.uwRed);
    addImageSync(slide, UW_CREST_WHITE, 1206, 11, 28, 50, { fit: "contain", alt: "University of Wisconsin-Madison crest" });
    return;
  }
  addImageSync(slide, UW_CREST_RED, 1186, 18, 44, 66, { fit: "contain", alt: "University of Wisconsin-Madison crest" });
}

function addSlideNumber(slide, slideNumber, color = palette.muted) {
  text(slide, `Slide ${String(slideNumber).padStart(2, "0")}`, 30, 680, 90, 20, {
    fontSize: 8,
    color,
    valign: "middle",
  });
}

function addBullets(slide, bullets, x, y, w, h, options = {}) {
  const theme = options.theme;
  const gap = options.gap ?? 16;
  const count = Math.max(1, bullets.length);
  const rowH = Math.min(options.maxRowHeight ?? 96, Math.max(50, (h - gap * (count - 1)) / count));
  bullets.forEach((bullet, index) => {
    const yy = y + index * (rowH + gap);
    rect(slide, x, yy + 11, 12, 12, options.dotColor ?? theme?.accent ?? palette.teal);
    const size = Math.min(options.fontSize ?? 24, bulletFont(bullet));
    text(slide, bullet, x + 30, yy, w - 30, rowH + 4, {
      fontSize: size,
      color: options.color ?? palette.ink,
      valign: "middle",
      insets: { left: 0, right: 8, top: 0, bottom: 0 },
    });
  });
}

function addLoopStrip(slide, deck, y = 604) {
  // The UW template keeps recurring chrome minimal; loop diagrams appear only
  // when they are the slide's proof object.
  return;
}

async function renderTitleSlide(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, SLIDE_SIZE.width, SLIDE_SIZE.height, "#ffffff");
  addUwMark(slide);
  text(slide, item.title, 40, 66, 720, 184, {
    fontSize: item.title.length > 82 ? 42 : 52,
    bold: true,
    color: palette.ink,
    valign: "middle",
  });
  rect(slide, 40, 268, 92, 7, theme.accent);
  text(slide, item.subtitle ?? "", 40, 296, 700, 70, {
    fontSize: 25,
    color: palette.uwGray,
    valign: "middle",
  });
  addBullets(slide, item.bullets ?? [], 48, 402, 600, 130, {
    theme,
    dotColor: palette.uwRed,
    color: palette.ink,
    fontSize: 23,
    gap: 14,
    maxRowHeight: 58,
  });
  if (item.image) {
    rect(slide, 742, 112, 438, 326, "#ffffff", "#d0d0d0", 1);
    await addImage(slide, item.image, 764, 132, 394, 286, { fit: "contain" });
  }
  rect(slide, 0, 596, 1280, 124, theme.accent);
  text(slide, "CEA-IRFM / Renaissance Fusion School on Stellarators", 42, 622, 570, 26, {
    fontSize: 18,
    bold: true,
    color: "#ffffff",
    valign: "middle",
  });
  text(slide, "Aix-en-Provence, 2026", 42, 650, 380, 24, {
    fontSize: 16,
    color: "#ffffff",
    valign: "middle",
  });
  text(slide, "Rogerio Jorge, University of Wisconsin-Madison", 780, 634, 390, 24, {
    fontSize: 16,
    bold: true,
    color: "#ffffff",
    align: "right",
    valign: "middle",
  });
  text(slide, `Repo: ${REPO_URL}`, 42, 672, 520, 18, {
    fontSize: 11,
    color: "#ffffff",
  });
  text(slide, `Docs: ${DOCS_URL}`, 780, 660, 390, 18, {
    fontSize: 11,
    color: "#ffffff",
    align: "right",
  });
  addSlideNumber(slide, slideNumber, "#ffffff");
  return slide;
}

function renderTransition(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, "#ffffff");
  addUwMark(slide);
  text(slide, theme.tag, 64, 58, 180, 26, {
    fontSize: 16,
    bold: true,
    color: theme.accent,
    valign: "middle",
  });
  rect(slide, 64, 94, 1080, 2, "#b7c5d9");
  text(slide, item.title, 170, 230, 900, 130, {
    fontSize: item.title.length > 65 ? 44 : 54,
    bold: true,
    color: palette.ink,
    align: "center",
    valign: "middle",
  });
  rect(slide, 564, 382, 148, 8, theme.accent);
  addBullets(slide, item.bullets ?? [], 238, 430, 820, 96, {
    theme,
    dotColor: theme.accent,
    color: palette.ink,
    fontSize: 24,
    maxRowHeight: 62,
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

async function renderFigure(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  const full = item.layout === "full";
  const imageBox = full
    ? { x: 72, y: 158, w: 1040, h: 438 }
    : { x: 52, y: 160, w: 776, h: 438 };
  rect(slide, imageBox.x, imageBox.y, imageBox.w, imageBox.h, "#ffffff", "#d0d0d0", 1);
  if (item.image) await addImage(slide, item.image, imageBox.x + 18, imageBox.y + 18, imageBox.w - 36, imageBox.h - 46, { fit: "contain" });
  if (!full) {
    text(slide, item.calloutTitle ?? "How to read it", 870, 170, 300, 28, {
    fontSize: 20,
    bold: true,
    color: theme.accent,
    });
    addBullets(slide, item.bullets ?? [], 866, 218, 340, 230, {
      theme,
      fontSize: 21,
      maxRowHeight: 74,
    });
    rect(slide, 866, 508, 340, 70, palette.lightGray, "#d0d0d0", 1);
    text(slide, item.caption ?? "Read the plot as a diagnostic, not as a new validated result.", 884, 522, 304, 38, {
      fontSize: 15,
      color: palette.uwGray,
      valign: "middle",
    });
  } else if (item.caption) {
    rect(slide, 126, 572, 900, 42, "#ffffff", "#e5e7eb", 1);
    text(slide, item.caption, 146, 582, 860, 24, {
      fontSize: 16,
      color: palette.uwGray,
      valign: "middle",
    });
  }
  addPageTitle(slide, deck, item, slideNumber, total);
  addFooter(slide, deck, slideNumber);
  return slide;
}

async function renderDemo(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, "#ffffff");
  addPageTitle(slide, deck, item, slideNumber, total);
  rect(slide, 80, 170, 420, 358, "#ffffff", "#d1d5db", 1);
  rect(slide, 80, 170, 420, 14, theme.accent);
  text(slide, "Notebook break", 112, 214, 300, 34, {
    fontSize: 25,
    bold: true,
    color: theme.accent,
  });
  text(slide, item.project ?? "", 112, 268, 340, 54, {
    fontSize: 18,
    color: palette.ink,
    typeface: "Aptos Mono",
    valign: "middle",
    fill: "#f8fafc",
    stroke: "#e5e7eb",
    strokeWidth: 1,
    insets: { left: 14, right: 14, top: 8, bottom: 8 },
  });
  addBullets(slide, item.bullets ?? [], 112, 354, 340, 116, {
    theme,
    fontSize: 21,
    maxRowHeight: 48,
  });
  if (item.image) await addImage(slide, item.image, 590, 174, 560, 330, { fit: "contain" });
  rect(slide, 590, 540, 560, 54, "#eef2ff", "#c7d2fe", 1);
  text(slide, item.caption ?? `Docs: ${DOCS_URL}`, 612, 553, 516, 28, {
    fontSize: 17,
    color: palette.navy,
    valign: "middle",
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

async function renderMovie(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  if (item.image) await addImage(slide, item.image, 86, 160, 760, 430, { fit: "contain" });
  addBullets(slide, item.bullets ?? [], 898, 210, 290, 184, {
    theme: deckThemes[deck.id],
    fontSize: 21,
    maxRowHeight: 58,
  });
  rect(slide, 898, 492, 290, 64, "#fff7ed", "#fed7aa", 1);
  text(slide, item.caption ?? "Use the static storyboard for reliable projection.", 914, 506, 258, 34, {
    fontSize: 15,
    color: "#9a3412",
    valign: "middle",
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderQuote(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, "#ffffff");
  addUwMark(slide);
  text(slide, item.title, 130, 190, 940, 148, {
    fontSize: item.title.length > 78 ? 42 : 52,
    bold: true,
    color: palette.ink,
    align: "center",
    valign: "middle",
  });
  rect(slide, 470, 374, 340, 8, theme.accent);
  addBullets(slide, item.bullets ?? [], 250, 430, 760, 90, {
    theme,
    dotColor: theme.accent,
    color: palette.ink,
    fontSize: 24,
    maxRowHeight: 48,
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderConcept(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  const bullets = item.bullets ?? [];
  bullets.forEach((bullet, index) => {
    const dense = bullets.length >= 4;
    const cols = dense ? 3 : bullets.length <= 2 ? bullets.length : 3;
    const gapX = dense ? 28 : 34;
    const gapY = 20;
    const cardW = dense
      ? (1112 - gapX * 2) / 3
      : bullets.length <= 2
        ? 520
        : 350;
    const startX = dense ? 84 : bullets.length <= 2 ? 110 : 78;
    const x = startX + (index % cols) * (cardW + gapX);
    const y = dense ? 164 + Math.floor(index / cols) * (138 + gapY) : 188;
    const h = dense ? 138 : 255;
    rect(slide, x, y, cardW, h, "#ffffff", "#d1d5db", 1);
    rect(slide, x, y, cardW, 12, index % 2 === 0 ? theme.accent : theme.accent2);
    text(slide, String(index + 1).padStart(2, "0"), x + 26, y + 36, 58, 40, {
      fontSize: dense ? 18 : 24,
      bold: true,
      color: index % 2 === 0 ? theme.accent : theme.accent2,
      valign: "middle",
    });
    text(slide, bullet, x + 26, y + (dense ? 78 : 94), cardW - 52, h - (dense ? 92 : 118), {
      fontSize: dense ? Math.min(18, bulletFont(bullet)) : bulletFont(bullet),
      color: palette.ink,
      valign: "middle",
      insets: { left: 0, right: 0, top: 8, bottom: 8 },
    });
  });
  rect(slide, 110, 492, 1060, 72, palette.lightGray, "#d0d0d0", 1);
  text(slide, "Class use", 136, 512, 150, 28, {
    fontSize: 18,
    bold: true,
    color: palette.uwRed,
  });
  text(slide, "Connect the concept to one objective, one plot, and one exercise.", 304, 512, 790, 34, {
    fontSize: 21,
    color: palette.ink,
    valign: "middle",
  });
  addLoopStrip(slide, deck);
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderMap(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  const labels = item.bullets ?? [];
  labels.forEach((label, index) => {
    const x = 86 + index * 382;
    rect(slide, x, 202, 312, 190, "#ffffff", "#d1d5db", 1);
    rect(slide, x, 202, 312, 12, index === 2 ? theme.accent : "#cbd5e1");
    text(slide, label.split(":")[0], x + 24, 235, 260, 32, {
      fontSize: 22,
      bold: true,
      color: index === 2 ? theme.accent : palette.slate,
      valign: "middle",
    });
    text(slide, label.includes(":") ? label.split(":").slice(1).join(":").trim() : label, x + 24, 292, 260, 70, {
      fontSize: 20,
      color: palette.ink,
      valign: "middle",
    });
  });
  text(slide, "Boundary", 150, 452, 146, 28, { fontSize: 18, bold: true, color: palette.muted, align: "center" });
  text(slide, "Derivations", 530, 452, 146, 28, { fontSize: 18, bold: true, color: palette.muted, align: "center" });
  text(slide, "Design loop", 910, 452, 146, 28, { fontSize: 18, bold: true, color: theme.accent, align: "center" });
  addLoopStrip(slide, deck);
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderWorkflow(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  const stages = ["Equilibrium", "Boozer spectrum", "Neoclassical", "Coils", "Turbulence", "Profiles", "Pareto"];
  stages.forEach((stage, index) => {
    const x = 74 + index * 165;
    const y = 215 + (index % 2) * 105;
    const active = index === 0 || item.title.toLowerCase().includes(stage.toLowerCase().split(" ")[0]);
    rect(slide, x, y, 134, 74, active ? theme.accent : "#ffffff", active ? theme.accent : "#cbd5e1", 1);
    text(slide, stage, x + 10, y + 13, 114, 44, {
      fontSize: stage.length > 13 ? 16 : 18,
      bold: active,
      color: active ? "#ffffff" : palette.ink,
      align: "center",
      valign: "middle",
    });
    if (index < stages.length - 1) {
      text(slide, ">", x + 138, y + 25, 26, 24, {
        fontSize: 20,
        color: palette.muted,
        align: "center",
      });
    }
  });
  const workflowBullets = item.bullets ?? [];
  addBullets(slide, workflowBullets, 120, workflowBullets.length > 2 ? 440 : 466, 980, workflowBullets.length > 2 ? 170 : 88, {
    theme,
    fontSize: workflowBullets.length > 2 ? 20 : 22,
    gap: workflowBullets.length > 2 ? 8 : 16,
    maxRowHeight: 44,
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderLadder(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  const bullets = item.bullets ?? [];
  const dense = bullets.length > 4;
  bullets.forEach((bullet, index) => {
    const col = dense ? index % 2 : 0;
    const row = dense ? Math.floor(index / 2) : index;
    const x = dense ? 104 + col * 540 : 212;
    const y = dense ? 170 + row * 78 : 175 + index * 100;
    const w = dense ? 430 : 840;
    const h = dense ? 58 : 74;
    rect(slide, x - 66, y + 14, 26, 26, index === bullets.length - 1 ? theme.accent : "#cbd5e1");
    if (!dense) rect(slide, x - 50, y + 52, 2, 54, index === bullets.length - 1 ? transparent : "#cbd5e1");
    rect(slide, x, y, w, h, "#ffffff", "#d1d5db", 1);
    text(slide, bullet, x + 24, y + 10, w - 48, h - 20, {
      fontSize: dense ? 20 : bulletFont(bullet),
      color: palette.ink,
      valign: "middle",
    });
  });
  text(slide, "Cost hierarchy", 1072, dense ? 534 : 490, 100, 28, {
    fontSize: 16,
    bold: true,
    color: theme.accent,
    align: "right",
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderWarning(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, "#fff7ed");
  const warningBullets = item.bullets ?? [];
  rect(slide, 88, 178, 1020, 410, "#ffffff", "#fed7aa", 2);
  rect(slide, 88, 178, 18, 410, palette.amber);
  text(slide, "Validation check", 132, 212, 420, 34, {
    fontSize: 23,
    bold: true,
    color: "#9a3412",
  });
  addBullets(slide, warningBullets, 134, 276, 890, warningBullets.length > 3 ? 218 : 178, {
    theme,
    dotColor: palette.amber,
    fontSize: warningBullets.length > 3 ? 20 : 22,
    gap: 8,
    maxRowHeight: 56,
  });
  rect(slide, 132, 512, 870, 1, "#fed7aa");
  text(slide, item.footer ?? "Validation rule: state the assumption, identify the metric, and explain what would change your mind.", 134, 528, 850, 40, {
    fontSize: 18,
    color: "#9a3412",
    valign: "middle",
  });
  addPageTitle(slide, deck, item, slideNumber, total);
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderExercise(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paperWarm);
  addPageTitle(slide, deck, item, slideNumber, total);
  rect(slide, 88, 168, 340, 350, theme.dark);
  text(slide, "Try this", 125, 212, 250, 50, {
    fontSize: 38,
    bold: true,
    color: "#ffffff",
  });
  text(slide, "5-10 minute classroom exercise", 128, 292, 235, 58, {
    fontSize: 22,
    color: "#e5e7eb",
    valign: "middle",
  });
  rect(slide, 128, 390, 230, 4, theme.accent2);
  addBullets(slide, item.bullets ?? [], 500, 198, 610, 220, {
    theme,
    fontSize: 25,
    maxRowHeight: 82,
  });
  rect(slide, 500, 462, 610, 64, "#eef2ff", "#c7d2fe", 1);
  text(slide, "Expected answer is qualitative: identify the tradeoff, not a magic optimum.", 522, 476, 566, 34, {
    fontSize: 18,
    color: palette.navy,
    valign: "middle",
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderCode(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  rect(slide, 96, 182, 700, 300, "#0f172a", "#334155", 1);
  rect(slide, 96, 182, 700, 34, "#1f2937", "#334155", 1);
  text(slide, item.label ?? "command surface", 118, 190, 320, 22, {
    fontSize: 14,
    color: "#e5e7eb",
  });
  const lines = item.commands ?? [
    "$ python scripts/run_smoke_tests.py",
    "$ python scripts/execute_all_notebooks.py",
    "$ python scripts/build_powerpoint_decks.mjs",
    "$ python scripts/check_release_ready.py",
  ];
  text(slide, lines.join("\n"), 124, 242, 620, 176, {
    fontSize: 23,
    color: "#d1fae5",
    typeface: "Aptos Mono",
    valign: "middle",
  });
  addBullets(slide, item.bullets ?? [], 840, 198, 300, 234, {
    theme,
    fontSize: 22,
    maxRowHeight: 70,
  });
  addLoopStrip(slide, deck);
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderTable(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  const rows = item.bullets ?? [];
  const x = 102;
  const y = 178;
  const w = 1040;
  const rowH = 76;
  const headers = ["Design question", "Optimization interpretation"];
  headers.forEach((header, index) => {
    rect(slide, x + index * (w / 2), y, w / 2, 46, theme.dark, "#ffffff", 0);
    text(slide, header, x + index * (w / 2) + 18, y + 9, w / 2 - 36, 24, {
      fontSize: 18,
      bold: true,
      color: "#ffffff",
      valign: "middle",
    });
  });
  rows.forEach((row, index) => {
    const yy = y + 46 + index * rowH;
    const [left, ...rightParts] = row.split(":");
    const right = rightParts.length ? rightParts.join(":").trim() : "Use it as a metric, constraint, or validation gate.";
    rect(slide, x, yy, w / 2, rowH, "#ffffff", "#e5e7eb", 1);
    rect(slide, x + w / 2, yy, w / 2, rowH, index % 2 ? "#f8fafc" : "#ffffff", "#e5e7eb", 1);
    text(slide, left.trim(), x + 18, yy + 12, w / 2 - 36, rowH - 24, {
      fontSize: 20,
      bold: true,
      color: theme.accent,
      valign: "middle",
    });
    text(slide, right, x + w / 2 + 18, yy + 12, w / 2 - 36, rowH - 24, {
      fontSize: bulletFont(right),
      color: palette.ink,
      valign: "middle",
    });
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderProject(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  rect(slide, 80, 168, 470, 460, "#ffffff", "#d1d5db", 1);
  rect(slide, 80, 168, 470, 14, theme.accent);
  text(slide, "Computational project", 110, 214, 360, 34, {
    fontSize: 25,
    bold: true,
    color: theme.accent,
  });
  text(slide, item.project ?? "notebook/script checkpoint", 110, 270, 390, 60, {
    fontSize: 19,
    color: palette.ink,
    typeface: "Aptos Mono",
    valign: "middle",
    fill: "#f8fafc",
    stroke: "#e5e7eb",
    strokeWidth: 1,
    insets: { left: 14, right: 14, top: 8, bottom: 8 },
  });
  addBullets(slide, item.bullets ?? [], 112, 356, 370, 134, {
    theme,
    fontSize: 22,
    maxRowHeight: 58,
  });
  const steps = item.steps ?? ["Open", "Run", "Change one knob", "Explain the plot"];
  steps.forEach((step, index) => {
    const y = 188 + index * 88;
    rect(slide, 662, y, 430, 58, index === 1 ? "#ecfdf5" : "#ffffff", "#d1d5db", 1);
    text(slide, String(index + 1), 686, y + 13, 34, 26, {
      fontSize: 18,
      bold: true,
      color: index === 1 ? palette.green : theme.accent,
      align: "center",
      valign: "middle",
    });
    text(slide, step, 742, y + 14, 300, 26, {
      fontSize: 23,
      bold: index === 1,
      color: palette.ink,
      valign: "middle",
    });
  });
  rect(slide, 660, 555, 432, 48, "#eef2ff", "#c7d2fe", 1);
  text(slide, "Deliverable: one figure and one defensible sentence.", 682, 568, 390, 22, {
    fontSize: 18,
    color: palette.navy,
    valign: "middle",
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderExplainer(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);

  rect(slide, 76, 164, 478, 336, "#f8fafc", "#d1d5db", 1);
  rect(slide, 76, 164, 478, 14, theme.accent);
  text(slide, item.term ?? "Concept", 106, 200, 410, 38, {
    fontSize: 31,
    bold: true,
    color: theme.accent,
    valign: "middle",
  });
  text(slide, item.definition ?? "", 106, 256, 404, 88, {
    fontSize: 23,
    color: palette.ink,
    valign: "middle",
  });
  if (item.equation) {
    rect(slide, 106, 376, 396, 64, "#ffffff", "#e5e7eb", 1);
    text(slide, item.equation, 122, 391, 364, 34, {
      fontSize: item.equation.length > 44 ? 23 : 28,
      bold: true,
      color: palette.navy,
      align: "center",
      valign: "middle",
      typeface: "Aptos Display",
    });
  }

  const cards = [
    ["Physical meaning", item.meaning],
    ["What the optimizer sees", item.optimizer],
    ["Failure mode", item.failure],
  ];
  cards.forEach(([label, body], index) => {
    const y = 166 + index * 116;
    rect(slide, 610, y, 548, 92, "#ffffff", "#d1d5db", 1);
    rect(slide, 610, y, 8, 92, index === 2 ? palette.amber : theme.accent);
    text(slide, label, 638, y + 14, 220, 24, {
      fontSize: 18,
      bold: true,
      color: index === 2 ? palette.amber : theme.accent,
      valign: "middle",
    });
    text(slide, body ?? "", 638, y + 42, 482, 36, {
      fontSize: 20,
      color: palette.ink,
      valign: "middle",
    });
  });

  rect(slide, 160, 546, 910, 52, theme.dark);
  text(slide, item.remember ?? "Remember the metric, the assumption, and the validation gate.", 186, 559, 858, 26, {
    fontSize: 20,
    bold: true,
    color: "#ffffff",
    align: "center",
    valign: "middle",
  });
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderSummary(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  addBullets(slide, item.bullets ?? [], 130, 190, 940, 270, {
    theme,
    fontSize: 28,
    maxRowHeight: 90,
  });
  rect(slide, 176, 508, 840, 54, theme.dark);
  text(slide, "A good optimization result is a design argument that survives new metrics.", 200, 521, 790, 26, {
    fontSize: 20,
    bold: true,
    color: "#ffffff",
    align: "center",
    valign: "middle",
  });
  addLoopStrip(slide, deck);
  addFooter(slide, deck, slideNumber);
  return slide;
}

function renderClosing(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, "#ffffff");
  rect(slide, 0, 0, 1280, 90, theme.accent);
  addUwMark(slide);
  text(slide, theme.tag, 64, 30, 180, 30, {
    fontSize: 18,
    bold: true,
    color: "#ffffff",
  });
  text(slide, item.title, 64, 150, 820, 108, {
    fontSize: item.title.length > 72 ? 44 : 54,
    bold: true,
    color: palette.ink,
    valign: "middle",
  });
  rect(slide, 66, 276, 92, 7, theme.accent);
  const bulletCount = (item.bullets ?? []).length;
  addBullets(slide, item.bullets ?? [], 74, bulletCount > 3 ? 330 : 342, 850, bulletCount > 3 ? 220 : 156, {
    theme,
    dotColor: theme.accent,
    color: palette.ink,
    fontSize: bulletCount > 3 ? 23 : 27,
    gap: 12,
    maxRowHeight: 64,
  });
  rect(slide, 68, 612, 812, 3, theme.accent);
  text(slide, "Repo lab handoff: rerun, perturb, compare, explain.", 72, 636, 820, 30, {
    fontSize: 22,
    color: palette.uwGray,
    valign: "middle",
  });
  text(slide, `${REPO_URL}\n${DOCS_URL}`, 888, 610, 300, 48, {
    fontSize: 13,
    color: palette.uwGray,
    align: "right",
    valign: "middle",
  });
  addSlideNumber(slide, slideNumber);
  return slide;
}

function addReference(slide, item) {
  if (!item.reference) return;
  text(slide, item.reference, 34, 638, 910, 18, {
    fontSize: 8,
    color: palette.muted,
    valign: "middle",
  });
}

async function renderGeneric(presentation, deck, item, slideNumber, total) {
  if (item.image) return renderFigure(presentation, deck, item, slideNumber, total);
  return renderConcept(presentation, deck, item, slideNumber, total);
}

async function renderSlide(presentation, deck, item, slideNumber, total) {
  let slide;
  switch (item.kind) {
    case "title":
      slide = await renderTitleSlide(presentation, deck, item, slideNumber, total);
      break;
    case "transition":
      slide = renderTransition(presentation, deck, item, slideNumber, total);
      break;
    case "figure":
      slide = await renderFigure(presentation, deck, item, slideNumber, total);
      break;
    case "demo":
      slide = await renderDemo(presentation, deck, item, slideNumber, total);
      break;
    case "movie":
      slide = await renderMovie(presentation, deck, item, slideNumber, total);
      break;
    case "quote":
      slide = renderQuote(presentation, deck, item, slideNumber, total);
      break;
    case "map":
      slide = renderMap(presentation, deck, item, slideNumber, total);
      break;
    case "workflow":
    case "diagram":
      slide = renderWorkflow(presentation, deck, item, slideNumber, total);
      break;
    case "ladder":
      slide = renderLadder(presentation, deck, item, slideNumber, total);
      break;
    case "warning":
      slide = renderWarning(presentation, deck, item, slideNumber, total);
      break;
    case "exercise":
      slide = renderExercise(presentation, deck, item, slideNumber, total);
      break;
    case "code":
      slide = renderCode(presentation, deck, item, slideNumber, total);
      break;
    case "table":
      slide = renderTable(presentation, deck, item, slideNumber, total);
      break;
    case "project":
      slide = renderProject(presentation, deck, item, slideNumber, total);
      break;
    case "explainer":
      slide = renderExplainer(presentation, deck, item, slideNumber, total);
      break;
    case "summary":
      slide = renderSummary(presentation, deck, item, slideNumber, total);
      break;
    case "closing":
      slide = renderClosing(presentation, deck, item, slideNumber, total);
      break;
    case "backup":
      slide = await renderGeneric(presentation, deck, item, slideNumber, total);
      break;
    case "concept":
    default:
      slide = await renderGeneric(presentation, deck, item, slideNumber, total);
      break;
  }
  addReference(slide, item);
  return slide;
}

async function writePreviewAndLayout(presentation, deck, slide, index, previewScale) {
  const previewDir = path.join(PREVIEW_ROOT, deck.id);
  const layoutDir = path.join(LAYOUT_ROOT, deck.id);
  const slideName = `slide-${String(index).padStart(2, "0")}`;
  await fs.mkdir(previewDir, { recursive: true });
  await fs.mkdir(layoutDir, { recursive: true });

  const previewPath = path.join(previewDir, `${slideName}.png`);
  const preview = await presentation.export({ slide, format: "png", scale: previewScale });
  await saveBlobToFile(preview, previewPath);

  let layoutPath = path.join(layoutDir, `${slideName}.layout.json`);
  try {
    const layout = await presentation.export({ slide, format: "layout" });
    await fs.writeFile(layoutPath, await layout.text(), "utf8");
  } catch (error) {
    layoutPath = undefined;
    console.warn(`layout export failed for ${deck.id} ${slideName}: ${error.message || error}`);
  }
  return { previewPath, layoutPath };
}

function makeContactSheet(deck, previewPaths) {
  const output = path.join(PPTX_DIR, "contact_sheets", `${deck.id}_contact_sheet.png`);
  const python = process.env.PYTHON || "python3";
  const result = spawnSync(
    python,
    [path.join(ROOT, "scripts", "make_pptx_contact_sheet.py"), "--output", output, "--cols", "5", ...previewPaths],
    { cwd: ROOT, encoding: "utf8" },
  );
  if (result.status !== 0) {
    throw new Error(
      [
        `Contact sheet generation failed for ${deck.id}.`,
        result.stdout.trim(),
        result.stderr.trim(),
      ]
        .filter(Boolean)
        .join("\n"),
    );
  }
  return output;
}

async function buildDeck(artifact, deck, previewScale) {
  const { Presentation, PresentationFile } = artifact;
  const presentation = Presentation.create({ slideSize: SLIDE_SIZE });
  const slides = [];
  for (let index = 0; index < deck.slides.length; index += 1) {
    const slide = await renderSlide(presentation, deck, deck.slides[index], index + 1, deck.slides.length);
    slides.push(slide);
  }

  const previewPaths = [];
  const layoutPaths = [];
  for (let index = 0; index < slides.length; index += 1) {
    const result = await writePreviewAndLayout(presentation, deck, slides[index], index + 1, previewScale);
    previewPaths.push(result.previewPath);
    if (result.layoutPath) layoutPaths.push(result.layoutPath);
  }

  await fs.mkdir(PPTX_DIR, { recursive: true });
  const output = path.join(PPTX_DIR, `${deck.id}.pptx`);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(output);
  const stat = await fs.stat(output);
  const contactSheet = makeContactSheet(deck, previewPaths);
  return {
    id: deck.id,
    title: deck.title,
    slideCount: slides.length,
    output,
    outputBytes: stat.size,
    previewDir: path.dirname(previewPaths[0]),
    layoutDir: path.dirname(layoutPaths[0]),
    contactSheet,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    console.log(usage());
    return;
  }
  const previewScale = args["preview-scale"] ? Number.parseFloat(args["preview-scale"]) : 0.5;
  if (!Number.isFinite(previewScale) || previewScale <= 0) {
    throw new Error("--preview-scale must be a positive number");
  }

  const spec = JSON.parse(await fs.readFile(SPEC_PATH, "utf8"));
  const selectedDecks = args.deck ? spec.decks.filter((deck) => deck.id === args.deck) : spec.decks;
  if (!selectedDecks.length) {
    throw new Error(`No matching deck for --deck ${args.deck}`);
  }

  const artifact = await importArtifactTool();
  await fs.mkdir(path.dirname(MANIFEST_PATH), { recursive: true });
  await fs.rm(PREVIEW_ROOT, { recursive: true, force: true });
  await fs.rm(LAYOUT_ROOT, { recursive: true, force: true });
  await fs.mkdir(PPTX_DIR, { recursive: true });

  const records = [];
  for (const deck of selectedDecks) {
    console.log(`Building ${deck.id} (${deck.slides.length} slides)`);
    records.push(await buildDeck(artifact, deck, previewScale));
  }

  const manifest = {
    builtAt: new Date().toISOString(),
    slideSize: SLIDE_SIZE,
    previewScale,
    artifactToolEntrypoint: artifactToolEntrypoint(),
    decks: records,
  };
  await fs.writeFile(MANIFEST_PATH, `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  console.log(JSON.stringify(manifest, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  console.error(usage());
  process.exit(1);
});
