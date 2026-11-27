---
name: Trợ lý Lab L3A — Cohort Dispatch Ledger
description: Calm, daylight-first lab support helpdesk and coordinator handoff ledger with on-demand trace drawer.
colors:
  signal-cobalt: "#1d4ed8"
  signal-cobalt-hover: "#1e40af"
  signal-cobalt-soft: "#eff6ff"
  signal-cobalt-hover-tint: "#dbeafe"
  signal-cobalt-border: "#bfdbfe"
  signal-cobalt-ring: "#93c5fd"
  navy-rail: "#132238"
  navy-rail-border: "#0b1626"
  lab-alabaster: "#f6f8fa"
  ledger-white: "#ffffff"
  slate-subtle: "#f8fafc"
  slate-border: "#d8dee6"
  slate-divider: "#e6ebf1"
  slate-hover-border: "#94a3b8"
  ink-primary: "#0f172a"
  ink-secondary: "#334155"
  ink-muted: "#475569"
  ink-placeholder: "#526071"
  rail-ink: "#f1f5f9"
  rail-muted: "#cbd5e1"
  verified-emerald: "#047857"
  verified-emerald-soft: "#ecfdf5"
  verified-emerald-border: "#a7f3d0"
  status-online-dot: "#34d399"
  status-live-dot: "#60a5fa"
  caution-amber: "#b45309"
  caution-amber-ink: "#78350f"
  caution-amber-soft: "#fffbeb"
  caution-amber-border: "#fde68a"
  caution-badge-bg: "#f59e0b"
  alert-crimson: "#b91c1c"
  alert-crimson-soft: "#fef2f2"
  alert-crimson-border: "#fecaca"
typography:
  display:
    fontFamily: "Be Vietnam Pro, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "26px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.02em"
  display-mobile:
    fontFamily: "Be Vietnam Pro, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.25
  headline:
    fontFamily: "Be Vietnam Pro, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "20px"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.015em"
  headline-mobile:
    fontFamily: "Be Vietnam Pro, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "19px"
    fontWeight: 700
    lineHeight: 1.25
  title:
    fontFamily: "Be Vietnam Pro, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "16px"
    fontWeight: 700
    lineHeight: 1.3
  body:
    fontFamily: "Be Vietnam Pro, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Be Vietnam Pro, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "13.5px"
    fontWeight: 600
    lineHeight: 1.35
  caption:
    fontFamily: "Be Vietnam Pro, Segoe UI, system-ui, -apple-system, sans-serif"
    fontSize: "12.5px"
    fontWeight: 500
    lineHeight: 1.4
  badge:
    fontFamily: "JetBrains Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "11.5px"
    fontWeight: 700
    lineHeight: 1.2
  mono:
    fontFamily: "JetBrains Mono, ui-monospace, Cascadia Mono, Consolas, monospace"
    fontSize: "12.5px"
    fontWeight: 500
    lineHeight: 1.4
rounded:
  tail: "4px"
  xs: "5px"
  sm: "6px"
  control: "8px"
  card: "12px"
  bubble: "16px"
  pill: "999px"
spacing:
  xs: "8px"
  sm: "12px"
  md: "16px"
  lg: "20px"
  xl: "24px"
components:
  button-primary:
    backgroundColor: "{colors.signal-cobalt}"
    textColor: "{colors.ledger-white}"
    rounded: "{rounded.control}"
    padding: "9px 18px"
  button-primary-hover:
    backgroundColor: "{colors.signal-cobalt-hover}"
  button-secondary:
    backgroundColor: "{colors.ledger-white}"
    textColor: "{colors.ink-primary}"
    rounded: "{rounded.control}"
    padding: "8px 13px"
  button-ghost:
    backgroundColor: "{colors.ledger-white}"
    textColor: "{colors.ink-secondary}"
    rounded: "{rounded.control}"
    padding: "7px 12px"
  card-ledger:
    backgroundColor: "{colors.ledger-white}"
    textColor: "{colors.ink-primary}"
    rounded: "{rounded.card}"
    padding: "16px 18px"
  input-field:
    backgroundColor: "{colors.slate-subtle}"
    textColor: "{colors.ink-primary}"
    rounded: "{rounded.control}"
    padding: "9px 12px"
---

# Design System: Trợ lý Lab L3A — Cohort Dispatch Ledger

## Overview

**Creative North Star: "Cohort Dispatch Ledger"**

Designed as a calm, low-clutter operational helpdesk for AI20K L3A learners in bright lab sessions and coordinators reviewing coach handoff drafts. The shell pairs a committed deep-navy navigation rail (`#132238`) with an expansive white workspace (`#ffffff`) centered at `780px` reading width, while keeping source verification and execution trace tucked inside an on-demand slide-over drawer (`Chi tiết & Trace`).

Instead of stacked telemetry banners, redundant card chrome, or label overload on every turn, answers read as clean prose anchored by a single quiet footer linking directly to source codes and trace metrics.

**Key Characteristics:**
- Calm two-column workspace by default (`248px` navy rail + `1fr` workspace), revealing technical trace and full source text only when requested.
- Minimal inline metadata per message: clean prose, clickable source citation chips, and compact handoff confirmation bars.
- Self-hosted `Be Vietnam Pro` (`400–700`) and `JetBrains Mono` (`400–700`) `.woff2` font files with zero external CDN dependency.
- Hairline dividers (`#e6ebf1`) and open whitespace replacing nested boxed cards.

## Colors

### Primary
- **Signal Cobalt** (`#1d4ed8`): Primary send/approve actions, active navigation tab, focused input borders, and inspected citation selection (`#1e40af` hover, `#eff6ff` / `#dbeafe` tint, `#bfdbfe` / `#93c5fd` borders).

### Secondary
- **Verified Emerald** (`#047857`, soft `#ecfdf5`, border `#a7f3d0`): Approved handoff status and active source validity badges (`#34d399` offline status dot).
- **Caution Amber** (`#b45309`, ink `#78350f`, soft `#fffbeb`, border `#fde68a`): Pending coordinator approval bars and queue count pill (`#f59e0b`).
- **Alert Crimson** (`#b91c1c`, soft `#fef2f2`, border `#fecaca`): Expired sources, inline submission errors, and rejected drafts.

### Neutral
- **Navy Rail** (`#132238`, border `#0b1626`): Persistent left navigation rail with light rail ink (`#f1f5f9`) and muted rail labels (`#cbd5e1`).
- **Ledger White** (`#ffffff`), **Lab Alabaster** (`#f6f8fa`), **Slate Subtle** (`#f8fafc`): Clean workspace surfaces separated by `#d8dee6` and `#e6ebf1` borders.
- **Ink Primary** (`#0f172a`), **Ink Secondary** (`#334155`), **Ink Muted** (`#475569`), **Ink Placeholder** (`#526071`): High-contrast daylight text hierarchy.

### Named Rules
**The Quiet Surface Rule.** Keep default chat turns free of boxed card borders and telemetry badges; reserve colored surfaces strictly for pending coach handoffs, active drawer inspection, and form errors.

## Typography

**Display & Body Font:** `Be Vietnam Pro` (self-hosted `.woff2` `400`, `500`, `600`, `700`)
**Label/Mono Font:** `JetBrains Mono` (self-hosted `.woff2` `400`, `500`, `600`, `700`)

**Character:** Clear Vietnamese prose hierarchy paired with `tabular-nums` monospace strictly for source codes, draft IDs, and trace timings.

### Hierarchy
- **Display** (`700`, `26px` desktop / `22px` mobile, `1.25` line-height, `-0.02em` tracking): Welcome screen headline (`h2`).
- **Headline** (`700`, `20px` desktop / `19px` mobile, `1.25` line-height, `-0.015em` tracking): Topbar workspace heading (`h1`).
- **Title** (`700`, `16px`, `1.3` line-height): Knowledge entries and drawer headings.
- **Body** (`400`, `15px`, `1.6`–`1.65` line-height, max `70ch`): Conversational replies and announcements.
- **Label & Caption** (`500`–`600`, `12.5px`–`13.5px`): Navigation tabs, filter pills, form labels, and footer source links.
- **Mono** (`500`–`600`, `12.5px`, `tabular-nums`): Citation codes, trace calls, and timestamps.

## Layout

Two-column desktop shell (`248px` left rail · `minmax(0, 1fr)` workspace centered at `780px` max content width) at `100dvh`. The `380px` Trace & Source drawer (`#inspectorPanel`) remains closed by default and slides over from the right when triggered by `Chi tiết & Trace`, a citation pill, or a `Trace (...)` footer link. Below `900px`, the rail also collapses into a slide-over drawer with `overflow-x: clip`.

## Elevation & Depth

Surfaces stay flat with `1px` borders (`#d8dee6` / `#e6ebf1`), reserving `box-shadow` only for the floating composer/cards (`0 1px 2px rgba(15, 23, 42, 0.04)`) and slide-over drawers (`0 10px 30px rgba(15, 23, 42, 0.14)`).

## Shapes

Consistent corner scale: `12px` (`card`) on welcome starter tiles, composer box, queue cards, and roster table; `8px` (`control`) on buttons, inputs, nav items, citation buttons, and handoff strip; `6px` (`sm`) / `5px` (`xs`) on compact inline code chips and skeleton bars; `999px` (`pill`) on filter pills and status badges.

## Components

### Buttons
- **Primary:** Signal Cobalt (`#1d4ed8`), `#ffffff` text, `8px` radius, `9px 18px` padding, `#1e40af` hover, `scale(0.98)` active press.
- **Secondary & Ghost:** `#ffffff` fill, `1px` `#d8dee6` or `#e6ebf1` border, `8px` radius, subtle `#f6f8fa` hover.

### Citation & Filter Pills
- **Citation link:** Calm `#f8fafc` button (`8px` radius, `1px` `#d8dee6` border) keeping source code `white-space: nowrap`; turns `#1d4ed8` fill with `#ffffff` text (`aria-pressed="true"`) only while inspected in the open drawer.
- **Filter pills:** `999px` pill buttons combining status label and live count (`Tất cả (2)`), inverting to `#132238` when active.

### Composer
- Single unified `#f8fafc` rounded container (`12px` radius, `1px` `#d8dee6` border) housing an auto-growing `<textarea>` and right-aligned `Gửi` CTA, transitioning cleanly to `#ffffff` and `#1d4ed8` border on focus.

### Slide-Over Inspector Drawer
- Off-canvas `380px` panel with pinned top summary (`Quyết định`, `Model`, `Công cụ / Token`) and independently scrolling `Nguồn đối chiếu` (with subtle `360ms` border highlight pulse when cross-linked) and `Nhật ký Trace`.

## Do's and Don'ts

### Do:
- **Do** keep conversation turns scannable as plain prose with at most one compact source footer and one inline action bar when a coach handoff draft exists.
- **Do** progressively disclose trace logs and full announcement excerpts inside the on-demand `Chi tiết & Trace` drawer.
- **Do** restore keyboard focus to the exact triggering button when closing any slide-over drawer.

### Don't:
- **Don't** render permanent 3-column telemetry dashboards or multi-step diagnostic banners inside everyday learner replies.
- **Don't** stack redundant status tags (`Mẫu demo`, token pills, or uppercase eyebrows) above headings or cards.
- **Don't** send external coach handoffs automatically without coordinator approval in the queue.
