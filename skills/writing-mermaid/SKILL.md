---
name: writing-mermaid
description: Use when creating or editing mermaid diagrams, especially with node labels containing special characters like forward slashes, square brackets, quotes, operators, or HTML
---

# Writing Mermaid Diagrams

## Overview

Mermaid diagram syntax has strict parsing rules that cause cryptic errors when special characters appear in node labels. Always quote node text containing forward slashes, square brackets, operators, quotes, or HTML.

## When to Use

- Creating flowcharts, sequence diagrams, state diagrams, or other mermaid charts
- Node labels contain file paths (`/dev/nvme0n1`)
- Node labels contain array notation (`[7:5]`, `[0]`)
- Node labels contain operators (`>=`, `===`, `?`)
- Node labels contain HTML (`<br>`)
- Debugging mermaid parse errors

## Core Rules

### Node Labels Must Be Quoted When Containing Special Characters

**Forward slashes** in file paths:
```mermaid
flowchart LR
    ❌ Drive1[/dev/nvme0n1]
    ✅ Drive1["/dev/nvme0n1"]
````

**Square brackets** in technical notation:

```mermaid
flowchart TD
    ❌ MPS_Bits[MPS Bits: [7:5]]
    ✅ MPS_Bits["MPS Bits: [7:5]"]
```

**Operators in decision nodes:**

```mermaid
flowchart TD
    ❌ Check{hit >= 0}
    ✅ Check{"hit >= 0"}
```

**HTML line breaks:**

```mermaid
flowchart TD
    ❌ Node[restore snapshot<br/>from point]
    ✅ Node["restore snapshot<br/>from point"]
```

### Quote Rules by Character Type

| Character        | Requires Quotes | Example           |
| ---------------- | --------------- | ----------------- |
| `/`              | Yes             | `"/dev/nvme0n1"`  |
| `[` `]`          | Yes             | `"Array[0]"`      |
| `>=`, `===`, `?` | Yes             | `"hit >= 0"`      |
| `<br>`           | Yes             | `"line<br>break"` |
| `"`              | Yes (escape)    | `"Say \"hello\""` |

**Rule:** When in doubt, quote the entire label.

## Common Errors and Fixes

| Error Message                | Cause                      | Fix                  |
| ---------------------------- | -------------------------- | -------------------- |
| `Lexical error on line X`    | Special chars in node text | Quote the node label |
| `Expecting 'SQE', got 'SQS'` | Nested brackets            | Wrap label in quotes |
| `Parse error on line X`      | Operators or HTML          | Quote label          |
| `Unrecognized text`          | Code-like syntax           | Simplify or quote    |

## Red Flags - Check Your Syntax

* File paths (`/home/user/file`)
* Bit ranges (`[7:5]`)
* API paths (`/api/v1/users`)
* Comparison expressions (`>=`, `===`)
* HTML (`<br>`)

All of these require quotes around node text.

## Testing Mermaid Diagrams

1. Ensure special characters are quoted
2. Quote any label containing operators or HTML
3. Verify arrows (`-->`) connect properly
4. Use simple node IDs (letters/numbers)

**Best practice:** quote labels proactively to avoid parser ambiguity.


