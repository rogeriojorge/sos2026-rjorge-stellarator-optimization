# PowerPoint decks

This folder contains the source specification and builder for the editable SOS 2026 PowerPoint decks.

Local Rogerio/PPPL reference decks were inspected for visual rhythm only.

No source deck images, PDFs, or PowerPoint files are copied into the public repo. The generated decks use repository figures and native editable artifact-tool shapes/text.

Build with:

```bash
node scripts/build_powerpoint_decks.mjs
```

Final PPTX files are written to `slides/pptx/`; per-slide previews are written to ignored generated folders; contact sheets are written to `slides/pptx/contact_sheets/` for review.
