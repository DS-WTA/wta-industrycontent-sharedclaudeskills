---
name: create-alt-text
description: Generate WCAG-aligned alt text (120 characters maximum) for one or more uploaded images. Trigger whenever the user says "Create alt text" (or close variants like "create alt texts", "write alt text for these", "alt text for this image") and has uploaded or attached images. Returns the alt texts in exactly the same order the images were uploaded.
---

# Create Alt Text

Write concise, useful alt text for uploaded images, following WCAG 2.x Success Criterion 1.1.1 (Non-text Content): the alt text must serve the *equivalent purpose* of the image, not just describe how it looks.

## Hard rules

1. **Maximum 120 characters per alt text**, including spaces and punctuation. Count every alt text before responding. If one is over 120, rewrite it shorter. Never truncate mid-word or mid-phrase; rephrase instead.
2. **Preserve upload order exactly.** The first image uploaded gets alt text #1, the second gets #2, and so on. Never reorder, group, merge, or skip images, even if some look similar, are duplicates, or would read better in a different sequence. People paste these results straight into a page or spreadsheet row by row, so a single swap puts the wrong text on the wrong image.
3. **One alt text per image.** If you can't tell how many images there are or in what order, check the uploaded files list (`/mnt/user-data/uploads`) and keep the order it presents.

## How to write each alt text

Decide what the image is *for* in the likely context, then write to that purpose:

- **Informative image (photo, illustration):** convey the key meaning in a short phrase or one sentence. Lead with the most important subject and action.
- **Functional image (icon, button, linked image):** describe the action or destination, not the picture. A magnifying glass icon is "Search", not "magnifying glass".
- **Image of text (banner, logo, screenshot of a quote):** include the text shown, as long as it fits. For a logo, use the organization's name, e.g. "Acme Corp logo".
- **Complex image (chart, graph, diagram, map):** state the type and the main takeaway, e.g. "Bar chart: online sales rose 40% from 2022 to 2024". If there's more detail than fits, add nothing extra in the alt text; the full description belongs in the page text.
- **Purely decorative image (flourish, divider, background texture):** return `alt=""` and mark it as decorative, so screen readers skip it.

## Style

- Don't start with "Image of", "Picture of", or "Photo of"; screen readers already announce an image. Mention the medium (photo, illustration, screenshot) only when it matters to meaning.
- Be specific and concrete ("Golden retriever catching a frisbee on a beach"), not vague ("A dog outside").
- Skip details that don't matter to purpose, such as exact colors or background items, unless they carry meaning.
- Use plain language and sentence case. End with a period only if the alt text is a full sentence.
- Don't guess names of real people from their appearance. Describe them by visible role or action unless the person is identified by text in the image or by the user.
- If the user gives context (where the image will be used, the audience), tailor the wording to it. Otherwise assume a general web page.

## Output format

Return only a numbered list, one line per image, in upload order. Each individual alt text should be able to be copied with one click, so that its as quick and easy as possible to use - it must be as simple as one click for one alt text, then another click for the next one and so on. Keep the character count visible so the limit is easy to verify:

```
1. [alt text] (N chars)
2. [alt text] (N chars)
3. alt="" (decorative)
```

Add nothing else unless needed. If an image is unreadable or fails to load, keep its slot and write `[Could not read this image]` so the numbering stays aligned with the upload order.

## Example

Three images uploaded in this order: a team photo, a search icon, a sales chart.

```
1. Five colleagues smiling around a conference table during a team meeting (71 chars)
2. Search (6 chars)
3. Bar chart showing online sales rising 40% from 2022 to 2024 (59 chars)
```