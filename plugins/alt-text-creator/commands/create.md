---
description: create alt text
---

## Name
alt-text-creator:create

## Synopsis
```
/alt-text-creator:create
```

## Description
Creates WCAG-compliant alt text, no more than 120 characters per image, using the process detailed in the `create-alt-text` skill.

## Implementation
Invoke the `create-alt-text` skill and follow its rules exactly.

## Return Value
Returns one alt text per uploaded image, in upload order, as described in the `create-alt-text` skill.
