# Design System Documentation: Architectural Precision

## 1. Overview & Creative North Star

### Creative North Star: "The Master’s Ledger"
For an Italian craftsman, a quote is more than a price; it is a document of intent, quality, and heritage. This design system moves away from generic "SaaS" aesthetics toward an **Editorial Architectural** style. We aim to replicate the feel of a high-end physical ledger—precise, authoritative, and impeccably organized—while ensuring extreme readability for the craftsman on a bustling job site.

By rejecting standard borders and "boxy" grids, we create a bespoke digital environment that feels premium. We utilize **intentional asymmetry**, wide margins, and **tonal layering** to guide the eye, ensuring that the "Preventivo" (quote) feels like a professional contract rather than a simple form.

---

## 2. Colors & Tonal Depth

This system is built on a foundation of deep professional blues and sophisticated neutrals. We do not use lines to separate ideas; we use light and shadow.

### The "No-Line" Rule
**Explicit Instruction:** Prohibit the use of 1px solid borders for sectioning or containers. Boundaries must be defined solely through background color shifts. 
- Use `surface-container-low` for secondary sections.
- Use `surface-container-lowest` (#ffffff) for primary content cards to make them "pop" against the `background` (#f8f9fa).

### Surface Hierarchy & Nesting
Treat the UI as physical layers of fine Italian paper.
- **Base Layer:** `surface` (#f8f9fa)
- **Primary Content Blocks:** `surface-container-lowest` (#ffffff)
- **Nested Detail Areas:** `surface-container-high` (#e7e8e9) 

### The "Glass & Gradient" Rule
To elevate the experience, floating elements (like mobile navigation bars or sticky quote totals) should use **Glassmorphism**:
- **Background:** `surface-container-lowest` with 80% opacity.
- **Blur:** `backdrop-filter: blur(12px)`.
- **CTA Soul:** Main action buttons should use a subtle linear gradient from `primary` (#002046) to `primary-container` (#1B365D) at a 135-degree angle to add a "sheen" of professional polish.

---

## 3. Typography: Editorial Authority

We use a pairing of **Manrope** for high-impact displays and **Inter** for functional data. This juxtaposition creates a sophisticated, modern Italian aesthetic.

- **Display & Headlines (Manrope):** These are your "Statement" pieces. Use `display-lg` for quote totals and `headline-md` for section titles like "Dettagli Progetto" (Project Details).
- **Body & Titles (Inter):** Inter provides the legibility required for technical line items. Use `title-sm` for field labels and `body-md` for description text.
- **Tone:** Headers should be high-contrast (`on-surface` #191c1d), while secondary information uses `on-surface-variant` (#44474e) to create a clear visual hierarchy.

---

## 4. Elevation & Depth

Hierarchy is achieved through **Tonal Layering**, not structural lines.

- **The Layering Principle:** To highlight a specific line item in a quote, do not use a border. Change the background of that specific row to `surface-container-highest` (#e1e3e4). This creates a "soft lift" that feels integrated.
- **Ambient Shadows:** When a card must float (e.g., a "Confirm Quote" modal), use an ultra-diffused shadow: `box-shadow: 0 12px 40px rgba(0, 32, 70, 0.08)`. Note the use of a blue-tinted shadow to match the primary brand color.
- **The "Ghost Border" Fallback:** If a boundary is strictly required for accessibility (e.g., in high-glare outdoor environments), use the `outline-variant` token at **15% opacity**. Never use a 100% opaque border.

---

## 5. Components

### Input Fields (Moduli)
- **Style:** No bottom line or full box. Use a subtle `surface-container-high` background with a `sm` (0.125rem) radius.
- **Active State:** On focus, the background shifts to `surface-container-lowest` with a 2px `primary` bottom-accent only.
- **Label:** Always use `label-md` in `on-surface-variant`.

### Buttons (Azioni)
- **Primary:** High-gloss gradient (Primary to Primary-Container). Use `xl` (0.75rem) roundedness for a modern, tactile feel. Label: "Crea Preventivo".
- **Secondary:** Transparent background with `on-primary-fixed-variant` text. No border. Use for "Annulla" (Cancel).

### The Artisan's Table (Tabella Voci)
- **Rule:** Forbid divider lines. 
- **Structure:** Use `spacing-4` (1rem) of vertical padding between items. Alternate row colors using `surface` and `surface-container-low` for high-speed scanning on mobile.
- **Typography:** Prices should be set in `title-md` using the `primary` color to ensure they are the first thing the craftsman sees.

### Quote Summary Chip
- **Context:** Used for "Approvato", "In Attesa", or "Scaduto".
- **Style:** Pill-shaped (`full` roundedness), using `secondary-container` backgrounds with `on-secondary-container` text.

---

## 6. Do’s and Don’ts

### Do:
- **Do** use Italian terminology that reflects the trade (e.g., "Manodopera" instead of "Labor", "Materiali" instead of "Items").
- **Do** maximize white space (`spacing-8` and above) between major quote sections to reduce cognitive load.
- **Do** use `primary-fixed` (#d6e3ff) as a subtle highlight background for selected text or active states.

### Don't:
- **Don't** use black (#000000). Use `on-surface` (#191c1d) for all text to maintain a premium, ink-like feel.
- **Don't** use standard 1px grey borders. This instantly makes the tool look like a generic template.
- **Don't** crowd the mobile view. If a table has more than 3 columns, collapse it into a "Card" view using the `surface-container-lowest` layering technique.

### Accessibility Note
In the field, glare is the enemy. Always ensure a contrast ratio of at least 7:1 for body text against backgrounds. Use the `on-error` (#ffffff) on `error` (#ba1a1a) for "Elimina" (Delete) actions to ensure zero ambiguity.