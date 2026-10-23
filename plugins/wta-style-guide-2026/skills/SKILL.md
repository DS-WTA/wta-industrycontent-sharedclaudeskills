---
name: "wta-style-guide"
description: "Apply the WTA (WiseTech Academy) Industry Style Guide v1.0 to any visual output: HTML interactions and widgets, SVG icons and graphics, diagrams, mockups, hero/image banners, scroll-animator and text-reveal assets, and the visual styling of slides and documents (colours, charts, tables). Trigger whenever the user asks to build, mock up, design, style, or review anything visual for WTA/WiseTech Academy, or mentions \"style guide\", \"brand colours\", \"WTA colours\", \"icon\", \"graphic\", \"mockup\", \"banner\", \"widget\", \"interaction\", or \"HTML\" in a WiseTech Academy context. Also trigger on \"check this against the style guide\". Read this skill BEFORE writing any markup, CSS, SVG, or slide theme; run the self-check at the end before delivering."
---

# WTA Industry Style Guide v1.0 — applied standard

Source of truth: *WTA Industry Style Guide v1.0* (WiseTech Academy Industry, internal GitHub Pages site). This skill encodes it so every visual output Claude produces conforms. Contacts for the guide: David Anderson (L&D Manager), Daniel Scott and Alex Yeo (Motion Graphics Designers).

**Guiding principle:** graphics serve the learner first. They must enhance learning (memorable, supports retention) and increase engagement. They must never confuse, distract, pull attention from the learning objective, or prioritise style over instructional clarity. If a visual only decorates, leave it out.

## How to use this skill

1. Identify the output type (Section A). Follow its rules.
2. Always apply Colours (B) and Typography (C).
3. For icons/SVG use D; for photos/illustrations/AI imagery E; for banners/widgets/export specs F; for video/screenshots G.
4. Before delivering, run the Self-check (H) and state briefly that it was run.
5. If another skill (e.g. `lxd-standards`, `lxd-coder`, `content-block-html-imports`) gives a conflicting value, see Section I.

---

## A. Output type → what applies

| Output | Must apply |
|---|---|
| HTML interaction / widget / LMS import | B tokens, C type scale + weights, D icon rules (no emoji, no outline-only), F widget dimensions, H |
| Standalone SVG icon | D in full (340×340 canvas, flat two-tone, 3px lines, edge-to-edge, solid fills), B primary set |
| Diagram / infographic / mockup | B (default WTA set first, tertiary/extended only when needed, approved pairings), C, D for any icons, H |
| Hero / image banner | F (1480×740, 2:1), E photography rules |
| Scroll animator / text reveal asset | F (340×340, SVG icons / PNG photos, transparent bg, edge-to-edge), D |
| Slides / Word visuals (charts, tables, callouts) | B palette in order of preference, C weights and hierarchy, D for icons, no gradients/3D/shadows in charts |
| Screenshots | G (1px Mid Grey #848484 border, crop tight, no sensitive data) |
| Video | G (16:9, 1920×1080, frame-rate rules, H264/MP4) |

---

## B. Colours

### Primary identity (use first, always)

| Name | Hex | RGB | Role |
|---|---|---|---|
| WiseTech Blue | `#1D1765` | 29 23 101 | Primary. Default text/foreground, icon fill, headings |
| Mid Sky Blue | `#A7CFF8` | 167 207 248 | Secondary. Icon accent, light backgrounds |
| White | `#FFFFFF` | 255 255 255 | Secondary. Backgrounds, reverse text |

### WTA colour set (default for all course graphics)

| Name | Hex | Tier |
|---|---|---|
| WiseTech Blue | `#1D1765` | Primary |
| Midnight | `#141E30` | Secondary |
| CargoWise Blue | `#371EE1` | Secondary |
| White | `#FFFFFF` | Secondary |
| Violet | `#B7B3FF` | Secondary |
| Mid Sky Blue | `#A7CFF8` | Secondary |

### Tertiary (illustrations needing more variety; check contrast first)

Pine `#244349` · Mint `#C6FFD1` · Highlighter `#EAFC88` · Cherry `#651D32` · Peach `#FFBE98`

### Approved background · foreground pairings

Navy(WiseTech Blue) · Sky Blue — Midnight · Mint — CargoWise Blue · Sky Blue — Violet · Navy — Sky Blue · Navy

Use these pairings for icons, cards, callouts and chart series before inventing new combinations.

### Extended palette (complex illustrations only — a supplement, never a replacement)

Cream Yellow `#FEFEC8`, Warm Sand `#F9E5D1`, Peach Sand `#F5D5B3`, Warm Brown `#A67354`, Amber `#FFCB47`, Orange `#E3831D`, Blush Pink `#F7DCE9`, Rose `#F2C4CD`, Dusty Rose `#EA9A97`, Terracotta `#A85451`, Magenta `#E24DC9`, Hot Pink `#E2356D`, Red `#C71A36`, Crimson `#9E1230`, Dark Red `#821831`, Plum `#7F1D59`, Burgundy Dark `#510B19`, Deep Purple `#441136`, Lime Green `#34C759`, Green `#2E8B57`, Olive `#64953E`, Teal Green `#0F8B8D`, Cyan `#01A5C0`, Light Cyan `#9EEDFA`, Cornflower `#75BDED`, Periwinkle `#7DABFF`, Blue `#4E85EA`, Dark Blue `#193468`, Indigo `#0B1374`, Deep Violet `#290C63`, Midnight (ext.) `#050B46`, Light Grey `#EFEFEF`, Warm Grey `#DCDCD7`, Mid Grey `#848484`, Dark Grey `#404041`, Near Black `#190105`.

Semantic defaults when a status colour is needed: success → Green `#2E8B57` (or Lime Green `#34C759`), warning → Amber `#FFCB47`, error → Red `#C71A36`, info → Blue `#4E85EA`. Neutral UI: Light Grey / Warm Grey / Mid Grey / Dark Grey.

### Rules

- Order of reach: WTA set → tertiary → extended. Never introduce a hex not in this skill.
- Check WCAG AA contrast (4.5:1 body text, 3:1 large text/UI) for every text/background pair. WiseTech Blue on White and White on WiseTech Blue both pass. Mid Sky Blue, Violet, Mint, Highlighter, Peach are **background/accent colours, not text colours on white**.
- No gradients, drop shadows, 3D or textures on icons and graphics.

### CSS tokens (paste into every HTML output)

```css
:root {
  /* Primary */
  --wta-blue:        #1D1765;
  --wta-sky:         #A7CFF8;
  --wta-white:       #FFFFFF;
  /* WTA set */
  --wta-midnight:    #141E30;
  --wta-cw-blue:     #371EE1;
  --wta-violet:      #B7B3FF;
  /* Tertiary */
  --wta-pine:        #244349;
  --wta-mint:        #C6FFD1;
  --wta-highlighter: #EAFC88;
  --wta-cherry:      #651D32;
  --wta-peach:       #FFBE98;
  /* Neutrals (extended) */
  --wta-grey-100:    #EFEFEF;
  --wta-grey-200:    #DCDCD7;
  --wta-grey-500:    #848484;
  --wta-grey-800:    #404041;
  --wta-black:       #190105;
  /* Semantic (extended) */
  --wta-success:     #2E8B57;
  --wta-warning:     #FFCB47;
  --wta-error:       #C71A36;
  --wta-info:        #4E85EA;
  /* Roles */
  --text:            var(--wta-blue);
  --text-muted:      var(--wta-grey-800);
  --bg:              var(--wta-white);
  --surface:         var(--wta-grey-100);
  --accent:          var(--wta-cw-blue);
  --accent-soft:     var(--wta-sky);
  --border:          var(--wta-grey-200);
  --focus-ring:      var(--wta-cw-blue);
}
```

---

## C. Typography

- Primary typeface: **DM Sans** (Regular 400). Fallback: **Arial**.
- `font-family: "DM Sans", Arial, sans-serif;` — always include Arial in the stack.
- Load when not on the LMS host page: `<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">`
- Slides/Word: DM Sans if installed, otherwise Arial. Never Calibri/Times/other.

### Type scale (do not invent one-off sizes)

| Label | Size | Use |
|---|---|---|
| Display | 36px | Hero title only |
| H1 | 28px | Primary section headings |
| H2 | 24px | Secondary structural headings |
| H3 | 20px | Tertiary structural headings |
| Subheading | 18px | Section intros, medium-emphasis headings |
| Body MD | 16px | Primary body, long-form |
| Body SM | 14px | Secondary copy, nav labels, supportive text |
| Caption SM | 13px | Badges, table headers, compact UI |
| Caption XS | 12px | Micro labels, helper metadata |

### Weights

400 body and long paragraphs · 500–600 headings, labels, UI emphasis · 700 sparingly, short emphasis only.

### Responsive

Step headings down at mobile breakpoints; keep body ≥16px readable. Preserve hierarchy spacing before adding new sizes.

```css
body { font-family: "DM Sans", Arial, sans-serif; font-size: 16px; line-height: 1.5; color: var(--text); -webkit-font-smoothing: antialiased; }
h1 { font-size: 28px; font-weight: 600; } h2 { font-size: 24px; font-weight: 600; } h3 { font-size: 20px; font-weight: 500; }
.subheading { font-size: 18px; font-weight: 500; } .body-sm { font-size: 14px; } .caption { font-size: 13px; } .caption-xs { font-size: 12px; }
@media (max-width: 600px) { h1 { font-size: 24px; } h2 { font-size: 20px; } h3 { font-size: 18px; } }
```

---

## D. Icons

Purpose: pace and structure information; support attention, not deliver core content. Conceptually connected to the text, not necessarily literal. Most common home: the scroll animator.

### Approved style

- Simple, clean geometric shapes; clear silhouette; flat, minimalist.
- **Two-tone fill** in WTA brand colours: WiseTech Blue `#1D1765` as the main fill, Mid Sky Blue `#A7CFF8` and/or White as the accent. (The official set uses exactly these three.)
- Solid fills only. Minimum detail; add complexity only where it adds relevance.

### Avoid

Gradients, shadows, 3D, textures, realistic rendering, **outline-only styles (no fill)**, emoji.

### Export spec

| Property | Value |
|---|---|
| Canvas | 340 × 340 px (scroll animator, text reveal). Official library icons are authored on a 128×128 viewBox — either is fine; keep square. |
| Format | SVG (from Illustrator by default) |
| Colour | Solid fills; primary colour + transparent or accent background; no outlines |
| Line weight | 3px consistent wherever lines are unavoidable |
| Edge to edge | Fill the allocated area vertically or horizontally; minimise whitespace |
| Background | Transparent |

### Official library (reuse before drawing new)

Box, Down, Factory, Folder, Gear, Globe, Invoice, Light Bulb, Location, Magnifying Glass, Money, Plane, Tick, Translate. Check WTA Image Search / SharePoint for the SVGs before creating a new icon.

### Exemplar (official "Box" icon — copy this construction style)

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-label="Box">
  <rect fill="#1D1765" x="8" y="8" width="112" height="112" rx="6" ry="6"/>
  <rect fill="#A7CFF8" x="50.3" y="8" width="27.4" height="32"/>
</svg>
```

Flat shapes, two fills, fills the canvas, rounded corners small (rx 6 on 128), no stroke.

### Inline UI icons in HTML

For small functional UI glyphs (check, warning, close) inside widgets, Material Icons Rounded are acceptable, coloured with WTA tokens and `aria-hidden="true"`. For any icon that is *content* (scroll animator, cards, feature icons) draw a WTA-style two-tone SVG instead. Never emoji.

---

## E. Photography, illustration, AI imagery

### Photography

Every photo must earn its place: does it help the learner understand or remember? If it decorates, distracts, or repeats the text, omit it.
Do: realistic balanced lighting, clear focal point; natural authentic real-world industry scenes; left-to-right visual flow with natural negative space.
Don't: too dark/overexposed; heavily processed or composited; visible logos or third-party branding.

### Illustrations

Style is **isometric** (depth without full 3D). Library: **Icograms** for all new work (log downloads in the tracking spreadsheet). Legacy isometric assets only on existing courses that already use them — never in new work. Custom assets allowed as substitutes only if they match the surrounding style.

### Sourcing order

Always check **WTA Image Search** first. Primary: Adobe Stock (preferred), iStock (credits limited), Icograms. Secondary: Unsplash, Pexels, The Noun Project (icons), Creative Commons. Working files → SharePoint project folder; final approved only → *For Development / DIY*.

### AI-generated imagery

Same standard as any image: relevant, believable, grounded in real industry context. **Must be reviewed by a technical reviewer before use.** Reject if: extra fingers / malformed faces, hands, feet; misspelled or hallucinated text on signs, labels, screens; lighting that doesn't match the scene; fuzzy or blended detail on screens, reflections, equipment; noticeably artificial.
AI presenters: **Synthesia only**, and only the three approved avatar/VO pairings — Nelly (Natalie Kind), Natalie (US Professional), Matt (EN US Strong). Pairings must not be swapped. WTA Industry only; other BUs need separate approval (contact David Anderson).

---

## F. Specifications (course element assets)

| Element | Dimensions | Format / notes |
|---|---|---|
| Hero banner | 1480 × 740 px (2:1) | First image on a module/page. Must reflect subject matter, ground learner in real context. Avoid busy centre focal points and overly detailed compositions without breathing room. |
| Image banner (inline) | 1480 × 740 px (2:1) | Breaks up text, reinforces a key concept. Context, not decoration. |
| Scroll animator | 340 × 340 px | SVG, transparent background, edge-to-edge fill. Simple and relevant. |
| Text reveal / card | 340 × 340 px | Icons SVG; photos PNG; white `#FFFFFF` bounding box 340×340. Images must survive being partly covered by text/icons. Wide cards (2:1): max 2 per chunk. |

### Formats

SVG — icons and vector graphics (default from Illustrator; OK for non-icon illustrations). PNG — assets needing transparency where SVG unsuitable. H264/MP4 — all video (Adobe Media Encoder, H264 Medium Adaptive; High Adaptive if quality insufficient).
**Deprecated (maintenance only, never new):** Lottie (→ MP4 with HTML imports), GIF (→ MP4).

### HTML widget defaults derived from the guide

- Card/container background White or Light Grey `#EFEFEF`; border 1px `#DCDCD7`; text WiseTech Blue; accent CargoWise Blue; soft accent Mid Sky Blue.
- No gradients, drop shadows beyond a subtle `0 1px 3px rgba(29,23,101,.08)`, or textures.
- Focus ring visible (CargoWise Blue, 2px). Respect `prefers-reduced-motion`.
- Icons per D. Fonts per C. Colours per B only.

---

## G. Video and screenshots

Video: 16:9, export 1920 × 1080, match frame rates when combining. Standard projects 25 fps (25 keep; 23.98/24/29.97/30 → 25 unless dialogue; 50 keep; 48/59.94/60 → 50). Synthesia projects 30 fps (29.97/30 keep; 23.98/24/25 → 30 unless dialogue; 59.94/60 keep; 48/50 → 60). Frame-rate changes alter audio pitch — correct or replace audio.

Screenshots: **1px stroke Mid Grey `#848484`** on every screenshot frame. Default 1920×1080 or crop tight to relevant UI while readable. PNG when transparency needed, JPG for full-screen captures. Consistent zoom across a module. Never include personal/sensitive data; never outdated UI.

---

## H. Self-check before delivery (run every time)

- [ ] Every colour used is in Section B; primary set reached for first; text/background pairs pass AA contrast.
- [ ] Font is DM Sans with Arial fallback; sizes come from the type scale; 400 body, 500–600 headings, 700 only for short emphasis.
- [ ] Icons: flat, two-tone WTA colours, solid fills, no outline-only, no gradients/shadows/3D, 3px lines if any, edge-to-edge, square canvas, SVG. No emoji anywhere.
- [ ] Asset dimensions match Section F for its element type.
- [ ] Photos/illustrations: earn their place, isometric/Icograms for new work, no legacy style, no third-party branding; AI imagery flagged for technical review.
- [ ] Screenshots have the 1px `#848484` border.
- [ ] No deprecated formats (GIF, Lottie).
- [ ] Nothing distracts from the learning objective.

Report the result in one line, e.g. "Style-guide self-check: passed (colours B, type C, icons D, spec F)". If something couldn't comply (e.g. a client-required colour), say so explicitly.

---

## I. Relationship to other WTA skills

`lxd-standards` / `lxd-coder` define interaction *mechanics* (card 720px, radius 1.25rem, play/replay chrome, iframe resize, launcher, accessibility) and several palettes. Where they conflict with this guide, this guide governs **colour and typography values**; they still govern mechanics. Known conflicts to resolve in favour of this skill unless the user says otherwise:

- Light WiseTech palette (`#0066cc`, `#001ba7`, `#355ca8`, `#8eabd6`, `rgba(176,204,255,.5)`) → replace with WTA tokens: text `#1D1765`, accent `#371EE1`, card border `#DCDCD7` or `#A7CFF8`, card bg `#FFFFFF`/`#EFEFEF` or Mid Sky Blue tint.
- Brand Dark palette (`#1E1A7A`, `#3B3AB0`, `#00BFB3`, `#ECEDF8`) → use `#1D1765`, `#371EE1`, `#A7CFF8`, `#EFEFEF`. Teal `#00BFB3` is not in the guide; nearest approved is Teal Green `#0F8B8D` (extended) or Cyan `#01A5C0`.
- Dark GitHub/Developer and third-party product skins are *simulations of external tools* — they may keep the tool's own colours inside the card; the outer card and any WTA chrome use this guide.
- lxd-standards says "Material Icons for all iconography" — keep for small functional UI glyphs; content icons follow Section D.
- Weight 700 for headings (lxd-standards) → prefer 500–600 per this guide.

Always tell the user when a conflict was resolved this way so the source skills can be updated.
