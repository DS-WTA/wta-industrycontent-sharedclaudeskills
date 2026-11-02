# Widget → source code patterns

These patterns come from the production page source (the Content column in the
dataForIndustryContent export, 7,269 pages). The converter emits exactly these
shapes. Use this file when checking output or handling a table the script does not know.

## Text
| Script | Source |
|---|---|
| Heading 2 | `<h2>Text</h2>` |
| Heading 3 / 4 | `<h3>` / `<h4>` |
| Body Text / Normal | `<p>…</p>` (bold → `<strong>`, italic → `<em>`, links → `<a href target="_blank" rel="noopener">`) |
| Bullets / numbered list | `<ul><li>…</li></ul>` / `<ol><li>…</li></ol>` |

## Image / Graphic table
```html
<img src="https://cdn.wisetechacademy.com/resources/wta/{FOLDER}/{FILE}.png" class="block-center" width="" height="" alt="{Alt text}">
```
Images are not wrapped in `<p>`; `<p>` is only for text.
```html
```
- `{FOLDER}` = the file name up to the `-M#P#` part (FDF-SAS-A1-M3P03a → FDF-SAS-A1). Reused
  assets keep their own course folder (N-AFRS-A1-M5P04d → N-AFRS-A1).
- Alignment: Center → `block-center`, Left → `float-left`, Right → `float-right`.
- Decorative = Yes → `alt=""`.
- Icon images that are used inside a scroll animator / text reveal / hotspot are not output on their own.

## Call-out
Call-out table Type, or the callout paragraph style:
| Type / style | Class |
|---|---|
| Primary (blue), Call out Box (pale blue), Call out box (pale grey) | `alert-primary` |
| Danger (red) | `alert-danger` |
| Success (green) | `alert-success` |
```html
<div class="alert-primary">
<p><strong>Scenario</strong></p>
<p>…</p>
</div>
```
A short first line (label such as "Scenario" or "Take note") becomes `<p><strong>…</strong></p>`.

### Case study (blue or grey callout)
When a blue (`alert-primary`) or grey (`highlight-box` / pale grey) callout's label line contains
"Case study", the class becomes `case-study`. The title and the first body paragraph share one `<p>`,
joined with `&nbsp;<br>`; any further paragraphs stay as their own `<p>`. Red and green callouts are unchanged.
```html
<div class="case-study">
<p><strong>Case study: Vanguard Logistics</strong>&nbsp;<br>Vanguard Logistics, described by FreightWaves as …</p>
</div>
```
Glossary links come only from green-highlighted text in the script (see SKILL.md steps 1b and 2d).

## Scroll animator (one per point)
```html
<wta-scroll-animator animation="fade-left" duration="500" repeat="false" trigger="auto" delay="200">
<wta-column-set><wta-column width="25%"><img src="…/FILE.svg" class="" width="" height="" alt="…"></wta-column><wta-column width="75%">
<h3>Point title</h3>
<p>…</p>
</wta-column></wta-column-set>
</wta-scroll-animator>
```
Scroll animator and text reveal images are SVG uploads: the path ends in `.svg`. Animation "Fade left" → `fade-left`; Repeat No/Yes → `false`/`true`; widths from the Column set rows.

## Image hotspot + Marker tables
```html
<wta-hotspot src="https://cdn.wisetechacademy.com/resources/wta/{FOLDER}/{FILE}.png">
<wta-hotspot-marker x="50" y="50" type="plus" title="…" answerstatus="neutral">
<p>…</p>
</wta-hotspot-marker>
</wta-hotspot>
```
The script only describes the marker location, so x/y are set to 50/50 and flagged.

## Text reveal (config table + Card tables)
```html
<wta-text-reveal paddingtop="auto" paddingbottom="auto" borderradius="auto" cardimageheight="180" widecards="false" backgroundcolour="#DCDCD7">
<wta-text-reveal-card src="…/FILE.png" height="" alt="…"><div slot="buttontext">Card title</div>
<div slot="trcontent"><p>…</p></div></wta-text-reveal-card>
</wta-text-reveal>
```

## Dropdown set (Word comment "DIY: Dropdown (this and others)" on a Heading 2)
Each heading in the set and its content becomes:
```html
<wta-expander class="">
<div slot="title">Heading</div>
<div slot="content">…</div>
</wta-expander>
```

## HTML import
```html
<wta-html-import contenteditable="false" url="/resources/wta/{SUBJECT}/{CODE}x/{CODE}x_launcher.html"></wta-html-import>
```
The URL is taken as written in the script. It is flagged if it is not a `_launcher.html`.

## Quick Quiz questions
```html
<wta-question qqtype="QuickQuiz" qids="44115" title="" contenteditable="false"></wta-question>
```
- Placed where the question table is, or at the "Add Quick Quiz N here" line when the script has one.
- Back-to-back quick-quiz tables are combined: `qids="44115, 44116"`.
- Final-assessment questions are not placed on the page.

## List block
```html
<ul class="course-resource">
<li><a href="…" target="_blank" rel="noopener">Resource title</a></li>
</ul>
```

## Other components seen in production (not in the current script template)
| Component | Source |
|---|---|
| Video | `<wta-video-23 contenteditable="false" videoid="…" token="…" aspect="ratio16x9" playerid=""></wta-video-23>` |
| Glossary link (added manually) | `<wta-glossary-link term="slug" text="Term" contenteditable="false">Term</wta-glossary-link>` |
| Zoom image | `<wta-zoom width="1900" height="auto"><p><img …></p></wta-zoom>` |
| PDF resource | `<wta-ibresource ibfileid="…" title="" text="…" filetype="pdf" contenteditable="false"></wta-ibresource>` |
| Image key | `<wta-image-keys data-style="inline" title="…"><wta-image-key label="…" color="#…" data-style="auto" contenteditable="false"></wta-image-key></wta-image-keys>` |
| Highlight box | `<div class="highlight-box">…</div>` |
| Case study | `<div class="case-study">…</div>` |
| Table | `<table class="default"><thead><tr><th scope="col">…</th></tr></thead><tbody>…</tbody></table>` |

## Glossary link (green highlight)
```html
<wta-glossary-link term="specialprocedures" text="special procedures"></wta-glossary-link>
```
`text` = the highlighted text as written. `term` = the matching glossary-table entry, lowercased with only letters and digits kept.
