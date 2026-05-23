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
const SLIDE_SIZE = { width: 1280, height: 720 };

const transparent = "#00000000";
const palette = {
  paper: "#f7faf8",
  paperWarm: "#fbfaf6",
  ink: "#111827",
  muted: "#4b5563",
  faint: "#e5e7eb",
  panel: "#ffffff",
  navy: "#172554",
  teal: "#0f766e",
  blue: "#2563eb",
  green: "#15803d",
  amber: "#d97706",
  coral: "#dc2626",
  violet: "#6d28d9",
  slate: "#334155",
};

const deckThemes = {
  lecture_1_geometry_metrics: {
    accent: palette.teal,
    accent2: palette.blue,
    dark: "#0b3b3a",
    tag: "Lecture 1",
    loopFocus: ["equilibrium", "Boozer spectrum", "metrics"],
  },
  lecture_2_coils_single_stage: {
    accent: palette.amber,
    accent2: palette.teal,
    dark: "#5a2f08",
    tag: "Lecture 2",
    loopFocus: ["coils", "B dot n", "single stage"],
  },
  lecture_3_transport_turbulence_metrics: {
    accent: palette.violet,
    accent2: palette.green,
    dark: "#35134b",
    tag: "Lecture 3",
    loopFocus: ["neoclassical", "turbulence", "validation"],
  },
  lecture_4_integrated_workflow: {
    accent: palette.blue,
    accent2: palette.coral,
    dark: "#12345b",
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
  return 40;
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
  text(slide, theme.tag, 58, 27, 170, 26, {
    fontSize: 15,
    bold: true,
    color: theme.accent,
    valign: "middle",
  });
  text(slide, `${slideNumber}/${total}`, 1152, 27, 70, 26, {
    fontSize: 14,
    color: palette.muted,
    align: "right",
    valign: "middle",
  });
  text(slide, item.title, 58, 58, 1060, 64, {
    fontSize: titleFont(item.title),
    bold: true,
    color: palette.ink,
    valign: "middle",
  });
  rect(slide, 58, 126, 160, 5, theme.accent);
  rect(slide, 225, 126, 62, 5, theme.accent2);
}

function addFooter(slide, deck, slideNumber) {
  const theme = deckThemes[deck.id];
  rect(slide, 58, 672, 1165, 1, "#d1d5db");
  text(slide, "SOS 2026 stellarator optimization teaching repo", 58, 686, 520, 22, {
    fontSize: 13,
    color: palette.muted,
  });
  text(slide, "cached -> tiny -> research", 925, 686, 210, 22, {
    fontSize: 13,
    color: palette.muted,
    align: "right",
  });
  rect(slide, 1150, 686, 38, 6, theme.accent);
  text(slide, String(slideNumber).padStart(2, "0"), 1196, 680, 32, 24, {
    fontSize: 13,
    color: palette.muted,
    align: "right",
  });
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
  const theme = deckThemes[deck.id];
  const stages = ["equilibrium", "Boozer", "neo", "coils", "turbulence", "profiles", "Pareto"];
  const x0 = 84;
  const w = 154;
  const gap = 8;
  stages.forEach((stage, index) => {
    const active = theme.loopFocus.some((focus) => stage.toLowerCase().includes(focus.toLowerCase().split(" ")[0]));
    const x = x0 + index * (w + gap);
    rect(slide, x, y, w, 40, active ? theme.accent : "#edf2f7", active ? theme.accent : "#cbd5e1", 1);
    text(slide, stage, x + 10, y + 7, w - 20, 24, {
      fontSize: 15,
      bold: active,
      color: active ? "#ffffff" : palette.slate,
      align: "center",
      valign: "middle",
    });
    if (index < stages.length - 1) {
      text(slide, ">", x + w + 1, y + 9, gap + 6, 20, {
        fontSize: 13,
        color: palette.muted,
        align: "center",
      });
    }
  });
}

async function renderTitleSlide(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, SLIDE_SIZE.width, SLIDE_SIZE.height, theme.dark);
  rect(slide, 515, 0, 765, 720, palette.paperWarm);
  rect(slide, 0, 0, 18, 720, theme.accent2);
  text(slide, theme.tag, 64, 52, 220, 34, {
    fontSize: 18,
    bold: true,
    color: "#d1fae5",
    valign: "middle",
  });
  text(slide, item.title, 62, 122, 418, 230, {
    fontSize: item.title.length > 78 ? 42 : 48,
    bold: true,
    color: "#ffffff",
    valign: "middle",
  });
  text(slide, item.subtitle ?? "", 66, 370, 400, 72, {
    fontSize: 24,
    color: "#f8fafc",
    valign: "middle",
  });
  addBullets(slide, item.bullets ?? [], 72, 466, 395, 144, {
    theme,
    dotColor: theme.accent2,
    color: "#f8fafc",
    fontSize: 19,
    gap: 8,
    maxRowHeight: 76,
  });
  if (item.image) {
    rect(slide, 570, 82, 636, 472, "#ffffff", "#d1d5db", 1);
    await addImage(slide, item.image, 590, 100, 596, 432, { fit: "contain" });
  }
  text(slide, "Computational design loop", 570, 582, 270, 28, {
    fontSize: 18,
    bold: true,
    color: theme.accent,
  });
  addLoopStrip(slide, deck, 626);
  text(slide, `${slideNumber}/${total}`, 1164, 36, 54, 24, {
    fontSize: 14,
    color: palette.muted,
    align: "right",
  });
  return slide;
}

function renderTransition(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, theme.dark);
  rect(slide, 0, 0, 1280, 16, theme.accent2);
  text(slide, theme.tag, 76, 88, 220, 32, {
    fontSize: 18,
    bold: true,
    color: "#dbeafe",
    valign: "middle",
  });
  text(slide, item.title, 74, 185, 890, 150, {
    fontSize: item.title.length > 65 ? 46 : 56,
    bold: true,
    color: "#ffffff",
    valign: "middle",
  });
  addBullets(slide, item.bullets ?? [], 84, 392, 800, 150, {
    theme,
    dotColor: theme.accent2,
    color: "#f8fafc",
    fontSize: 25,
    maxRowHeight: 62,
  });
  text(slide, `${slideNumber}/${total}`, 1160, 660, 60, 24, {
    fontSize: 14,
    color: "#cbd5e1",
    align: "right",
  });
  return slide;
}

async function renderFigure(presentation, deck, item, slideNumber, total) {
  const slide = presentation.slides.add();
  const theme = deckThemes[deck.id];
  rect(slide, 0, 0, 1280, 720, palette.paper);
  addPageTitle(slide, deck, item, slideNumber, total);
  rect(slide, 58, 154, 735, 446, "#ffffff", "#d1d5db", 1);
  if (item.image) await addImage(slide, item.image, 78, 174, 695, 392, { fit: "contain" });
  text(slide, "How to read it", 850, 165, 320, 28, {
    fontSize: 20,
    bold: true,
    color: theme.accent,
  });
  addBullets(slide, item.bullets ?? [], 842, 215, 340, 284, {
    theme,
    fontSize: 22,
    maxRowHeight: 88,
  });
  rect(slide, 842, 526, 334, 58, "#fff7ed", "#fed7aa", 1);
  text(slide, "Teaching rule: the plot is a design diagnostic, not decoration.", 862, 538, 294, 34, {
    fontSize: 16,
    color: "#9a3412",
    valign: "middle",
  });
  addLoopStrip(slide, deck);
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
  rect(slide, 110, 492, 1060, 72, "#eef2ff", "#c7d2fe", 1);
  text(slide, "Optimization view", 136, 512, 190, 28, {
    fontSize: 18,
    bold: true,
    color: palette.navy,
  });
  text(slide, "Turn each physical idea into an objective, constraint, validation gate, or reason to stop.", 330, 512, 790, 34, {
    fontSize: 22,
    color: palette.navy,
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
  addPageTitle(slide, deck, item, slideNumber, total);
  const warningBullets = item.bullets ?? [];
  rect(slide, 88, 178, 1020, 410, "#ffffff", "#fed7aa", 2);
  rect(slide, 88, 178, 18, 410, palette.amber);
  text(slide, "Failure mode / guardrail", 132, 212, 420, 34, {
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
  text(slide, "Classroom stance: label approximations and use cached mode when the live code is too expensive.", 134, 528, 850, 40, {
    fontSize: 18,
    color: "#9a3412",
    valign: "middle",
  });
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
  text(slide, "cached-mode command surface", 118, 190, 320, 22, {
    fontSize: 14,
    color: "#e5e7eb",
  });
  const lines = [
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
  const steps = ["Open", "Run cached", "Change one knob", "Explain the plot"];
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
  rect(slide, 0, 0, 1280, 720, theme.dark);
  text(slide, theme.tag, 78, 64, 180, 30, {
    fontSize: 18,
    bold: true,
    color: "#dbeafe",
  });
  text(slide, item.title, 78, 142, 820, 108, {
    fontSize: item.title.length > 72 ? 44 : 54,
    bold: true,
    color: "#ffffff",
    valign: "middle",
  });
  const bulletCount = (item.bullets ?? []).length;
  addBullets(slide, item.bullets ?? [], 88, bulletCount > 3 ? 300 : 318, 850, bulletCount > 3 ? 250 : 156, {
    theme,
    dotColor: theme.accent2,
    color: "#f8fafc",
    fontSize: bulletCount > 3 ? 23 : 27,
    gap: 12,
    maxRowHeight: 64,
  });
  rect(slide, 84, 626, 812, 4, theme.accent2);
  text(slide, "Repo lab handoff: rerun, perturb, compare, explain.", 88, 648, 820, 30, {
    fontSize: 24,
    color: "#e5e7eb",
    valign: "middle",
  });
  text(slide, `${slideNumber}/${total}`, 1156, 662, 64, 24, {
    fontSize: 14,
    color: "#cbd5e1",
    align: "right",
  });
  return slide;
}

async function renderGeneric(presentation, deck, item, slideNumber, total) {
  if (item.image) return renderFigure(presentation, deck, item, slideNumber, total);
  return renderConcept(presentation, deck, item, slideNumber, total);
}

async function renderSlide(presentation, deck, item, slideNumber, total) {
  switch (item.kind) {
    case "title":
      return renderTitleSlide(presentation, deck, item, slideNumber, total);
    case "transition":
      return renderTransition(presentation, deck, item, slideNumber, total);
    case "figure":
      return renderFigure(presentation, deck, item, slideNumber, total);
    case "map":
      return renderMap(presentation, deck, item, slideNumber, total);
    case "workflow":
    case "diagram":
      return renderWorkflow(presentation, deck, item, slideNumber, total);
    case "ladder":
      return renderLadder(presentation, deck, item, slideNumber, total);
    case "warning":
      return renderWarning(presentation, deck, item, slideNumber, total);
    case "exercise":
      return renderExercise(presentation, deck, item, slideNumber, total);
    case "code":
      return renderCode(presentation, deck, item, slideNumber, total);
    case "table":
      return renderTable(presentation, deck, item, slideNumber, total);
    case "project":
      return renderProject(presentation, deck, item, slideNumber, total);
    case "summary":
      return renderSummary(presentation, deck, item, slideNumber, total);
    case "closing":
      return renderClosing(presentation, deck, item, slideNumber, total);
    case "backup":
      return renderGeneric(presentation, deck, { ...item, title: `Appendix: ${item.title}` }, slideNumber, total);
    case "concept":
    default:
      return renderGeneric(presentation, deck, item, slideNumber, total);
  }
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
