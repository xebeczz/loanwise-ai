---
name: Institutional Intelligence
colors:
  surface: '#f8f9ff'
  surface-dim: '#ccdbf4'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d4e4fc'
  on-surface: '#0d1c2e'
  on-surface-variant: '#44474d'
  inverse-surface: '#223144'
  inverse-on-surface: '#eaf1ff'
  outline: '#75777d'
  outline-variant: '#c5c6cd'
  surface-tint: '#505f78'
  primary: '#000e23'
  on-primary: '#ffffff'
  primary-container: '#14243a'
  on-primary-container: '#7c8ba6'
  inverse-primary: '#b7c7e4'
  secondary: '#2f5daa'
  on-secondary: '#ffffff'
  secondary-container: '#85adff'
  on-secondary-container: '#003f8a'
  tertiary: '#00110e'
  on-tertiary: '#ffffff'
  tertiary-container: '#002924'
  on-tertiary-container: '#009c8b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d4e3ff'
  primary-fixed-dim: '#b7c7e4'
  on-primary-fixed: '#0b1c32'
  on-primary-fixed-variant: '#38475f'
  secondary-fixed: '#d8e2ff'
  secondary-fixed-dim: '#adc6ff'
  on-secondary-fixed: '#001a41'
  on-secondary-fixed-variant: '#0b4490'
  tertiary-fixed: '#76f8e3'
  tertiary-fixed-dim: '#56dbc7'
  on-tertiary-fixed: '#00201c'
  on-tertiary-fixed-variant: '#005047'
  background: '#f8f9ff'
  on-background: '#0d1c2e'
  surface-variant: '#d4e4fc'
typography:
  display-lg:
    fontFamily: Manrope
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Manrope
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-xl:
    fontFamily: Manrope
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Manrope
    fontSize: 22px
    fontWeight: '600'
    lineHeight: 30px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Manrope
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '600'
    lineHeight: 18px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.03em
  code-sm:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.5rem
  gutter-mobile: 0.75rem
  margin: 2rem
  margin-mobile: 1rem
  space-xxs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
  space-2xl: 2rem
  space-3xl: 3rem
---

## Brand & Style

This design system establishes an institutional-grade, analytical interface built specifically for mission-critical machine learning underwriting and financial risk modeling. The aesthetic balances executive-level clarity with dense, high-frequency operational capability.

### Brand Personality & Emotional Drivers
- **Unwavering Authority & Fiduciary Rigor:** Evokes institutional competence and sovereign reliability. Decisions made within the system must project absolute mathematical credibility.
- **Cognitive Clarity over Flash:** Elimination of superfluous visual noise allows credit analysts and risk officers to interpret probabilistic scores, anomaly metrics, and audit trails without fatigue.
- **Deterministic Modernism:** Inspired by high-end financial architecture (Stripe Press, Brex Enterprise, Plaid Core), combining crisp geometry, surgical border definitions, and strict information zoning.

### Visual Style
- **Corporate High-Precision Modernism:** Grounded on a cool architectural background, clean tabular surfaces, hairline structural dividers, and calculated use of high-chroma data signifiers.
- **Density & Ergonomics:** Compact typographic line metrics and standardized data display grids built to handle high-dimensional risk factors simultaneously without structural degradation.

## Colors

The palette is engineered around high contrast, institutional depth, and semantic clarity for critical decision-making.

### Palette Architecture
- **Primary Navy (`#14243A`):** The structural core. Used for dominant typographic weight, global application framing, and primary structural emphasis.
- **Secondary Royal Blue (`#315EAB`):** Interactive focal points, active state highlights, primary interactive triggers, and navigational active indicators.
- **Accent Teal (`#24B8A5`):** Machine learning indicators, model confidence scores, algorithmic feature flags, and real-time processing telemetry.
- **Background Slate Tint (`#F4F7FB`):** A cool, low-strain canvas foundation that sets off high-purity card surfaces with crisp contrast.
- **Surface Pure White (`#FFFFFF`):** Work surfaces, analytical card modules, data grid containers, and overlay dialogs.
- **Neutral / Muted Slate (`#718096`):** Secondary metadata, column labels, micro-copy, and passive icon strokes.
- **Hairline Border (`#E2E8F0`):** Defines bounding boxes and spatial boundaries without asserting visual weight.

### Semantic Triage Indicators
- **Success (`#16A36A`):** Prime credit ratings, automated pass criteria, low-risk classification.
- **Warning (`#E9A23B`):** Manual underwriter intervention required, edge-case scores, debt-to-income boundary warnings.
- **Danger (`#DC5353`):** High delinquency risk, fraud alert detections, automated policy rejections.

## Typography

The typographic hierarchy is divided into structural narrative elements (`Manrope`) and analytical data layers (`Inter` + `JetBrains Mono`).

### Rules for Numerical and Data Display
- All numerical figures, currency displays, risk scores, and interest rates must enforce open-type tabular lining numerals (`tnum`, `lnum`) to ensure vertical grid alignment across comparison columns.
- Uppercase micro-labels (`label-sm`) require tracking expansions to guarantee instant legibility when contextualizing complex telemetry charts and pipeline headers.
- Code-level audit identifiers, SHAP values, and API transaction payloads default strictly to `code-sm` to prevent misinterpretation of mathematical values and hash keys.

## Layout & Spacing

The layout is built upon an uncompromising 8px baseline grid (with a 4px half-step for micro-component positioning and dense data tables).

### Layout System
- **Desktop (>= 1280px):** 12-column fluid grid locked within a maximum 1600px analytical canvas. Primary sidebars use a fixed 260px or 80px collapsed rail, allowing risk dashboards and decision queues to utilize the full variable area.
- **Tablet (768px - 1279px):** 8-column layout. Multi-column decision workspaces stack into primary and contextual side drawers. Margins scale to `1.5rem`.
- **Mobile (< 768px):** 4-column layout. High-density data displays shift into accordion-based risk breakdowns and horizontal snap-scroll cards. Margins compress to `1rem`.

### Spatial Discipline
- Margins and gutters govern the outer boundary of modules. Internal card padding enforces an exact relationship: 16px (`space-lg`) for dense sub-modules, 24px (`space-xl`) for primary decision summaries.
- Vertical space between discrete card widgets is strictly decoupled from component-internal padding to retain spatial rhythm across viewport changes.

## Elevation & Depth

Visual hierarchy leverages flat planes, razor-thin structural borders, and subtle diffuse shadows, avoiding heavy drops or skeuomorphic treatments.

### Layer Tiers
- **Tier 0 (App Canvas):** `#F4F7FB`. The root base plane.
- **Tier 1 (Surface Cards & Tables):** `#FFFFFF` paired with an outline of `1px solid #E2E8F0` and an ultra-subtle ambient shadow: `box-shadow: 0 1px 3px 0 rgba(20, 36, 58, 0.04), 0 1px 2px -1px rgba(20, 36, 58, 0.02)`.
- **Tier 2 (Interactive Floating & Hover States):** Lifted cards and action bars elevate slightly via: `box-shadow: 0 4px 6px -1px rgba(20, 36, 58, 0.06), 0 2px 4px -2px rgba(20, 36, 58, 0.04)` with border transitioning to `#CBD5E1`.
- **Tier 3 (Dropdown Menus & Overlays):** Detached popovers and dropdowns utilize: `box-shadow: 0 10px 15px -3px rgba(20, 36, 58, 0.08), 0 4px 6px -4px rgba(20, 36, 58, 0.04)`.
- **Tier 4 (Modal Audit Windows):** Critical overrides and override verification dialogs sit over a backdrop overlay: `rgba(20, 36, 58, 0.45)` with `backdrop-filter: blur(4px)`.

## Shapes

The geometric architecture is crisp, grounded, and modern. Standard elements utilize a disciplined 8px (`0.5rem`) radius to convey modern banking software precision without looking toy-like or sterile.

### Corner Radius Allocation
- **Precision Inputs, Buttons, & Field Shells:** 8px (`0.5rem`).
- **Dashboard Cards, Data Modules, & Grid Enclosures:** 12px (`rounded-lg`, `0.75rem`) to frame nested content cleanly.
- **Pill Badges & Tabs:** Full border-radius (`9999px`) reserved specifically for status tags, metadata chips, and model score badges.
- **Inner Nested Sub-Containers:** 6px to maintain nested concentric corner geometry inside 12px cards.

## Components

### Buttons
- **Primary:** Background `#14243A`, text `#FFFFFF`, border `transparent`. Hover: `#315EAB`. Height: 36px (Compact) or 40px (Standard). Font: `Inter` 14px/600.
- **Secondary:** Background `#FFFFFF`, text `#172B4D`, border `1px solid #E2E8F0`. Hover: `#F8FAFC`, border `#CBD5E1`.
- **Tertiary / Ghost:** Background `transparent`, text `#315EAB`. Hover: `#F4F7FB`.
- **Destructive:** Background `#DC5353`, text `#FFFFFF`. Hover: `#B91C1C`.

### Cards & Analytical Panels
- White `#FFFFFF` background, `border: 1px solid #E2E8F0`, corner radius `12px`.
- Card headers feature clear separation: a 16px bottom padding with optional subtle horizontal separator `1px solid #F1F5F9`.
- Header title in `headline-md` (`Manrope`, 600) with supporting metadata or timestamp in `body-sm` (`#718096`).

### Data Tables
- Header row height: 38px, background `#F8FAFC`, text `#718096`, `label-sm` uppercase, `letter-spacing: 0.04em`.
- Data rows: height 48px, border-bottom `1px solid #F1F5F9`, alternating hover state background `#F8FAFC`.
- All monetary and percentage fields right-aligned with tabular numerals.
- Action column pinned right with icon-only ghost buttons.

### Status Badges & Chips
- Enclosed in full pill radius (`9999px`). Internal padding: `2px 8px` for compact, `4px 12px` for standard.
- **Approved / Prime:** Surface `#ECFDF5`, text `#16A36A`, border `1px solid #A7F3D0`.
- **Review / Caution:** Surface `#FFFBEB`, text `#D97706`, border `1px solid #FDE68A`.
- **Declined / Risk Alert:** Surface `#FEF2F2`, text `#DC5353`, border `1px solid #FECACA`.
- **Model Confident:** Surface `#F0FDFA`, text `#0F766E`, border `1px solid #99F6E4`.

### Sleek Pill Tabs
- Contained segmented control shell: background `#E2E8F0`, padding `3px`, radius `9999px`.
- Active segment: `#FFFFFF`, text `#14243A`, shadow `0 1px 2px rgba(20, 36, 58, 0.06)`, radius `9999px`.
- Inactive segment: text `#718096`, hover text `#14243A`, transparent background.

### Form Controls
- Text inputs and dropdowns: background `#FFFFFF`, border `1px solid #E2E8F0`, height 38px, radius `8px`, typography `body-md`.
- Focus state: border `#315EAB`, ring `2px solid rgba(49, 94, 171, 0.15)`.
- Checkboxes and Radio: 16px square/circle, border `#CBD5E1`. Checked state: `#14243A` with crisp white inner check/dot.

### Iconography
- SVG-only (Lucide style) with a consistent `1.75px` stroke weight.
- Never use emojis or raster pictorial assets in operational views.
- Size standard: 16x16px for inline data indicators; 20x20px for primary navigation items.