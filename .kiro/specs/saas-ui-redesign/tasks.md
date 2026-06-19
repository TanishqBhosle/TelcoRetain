# Implementation Plan: SaaS UI Redesign

## Overview

This plan transforms TelcoRetain's rapid-prototype UI into a polished SaaS product by implementing a design token system, consistent component styling, reusable state components, refined navigation, elevated dashboards, and conversion-quality marketing/auth pages. All work targets the existing `src/styles.css` file and React components in `src/components/`, `src/panels/`, and `src/pages/`.

## Tasks

- [x] 1. Design Token System Foundation
  - [x] 1.1 Define color, spacing, typography, radius, shadow, and transition tokens on `:root`
    - Add all CSS custom properties to `src/styles.css` under a clearly commented `/* 1. DESIGN TOKENS */` section
    - Include primary, primary-hover, primary-subtle, neutral-50 through neutral-900, success, warning, danger, surface token groups
    - Include spacing scale (4px to 64px), typography scale (xs through 4xl), border-radius (sm through 2xl), shadow (sm through xl), and transition durations (fast, normal, slow)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

  - [x] 1.2 Define admin dark theme token overrides scoped to `.admin-shell`
    - Add `/* 2. DESIGN TOKENS — Admin dark theme override */` section in `src/styles.css`
    - Override color-primary, neutral scale (inverted), success, warning, danger, surface, border tokens with dark-appropriate values
    - Ensure `.admin-shell` class is applied to the AdminAppShell root container in `src/panels/admin/AdminAppShell.tsx`
    - _Requirements: 1.7_

- [x] 2. Base Typography and Component Styling
  - [x] 2.1 Implement base typography and heading hierarchy
    - Add `/* 3. BASE RESET & TYPOGRAPHY */` section in `src/styles.css`
    - Set h1 font-weight 700–800, h2 font-weight 600; line-height 1.2 for headings, 1.5 for body
    - Define heading font sizes: h1 ≥ 30px, h2 ≥ 24px, h3 ≥ 20px, body ≥ 16px
    - Apply letter-spacing -0.01em for headings larger than 24px
    - Use neutral-500 for secondary text with minimum 3:1 contrast
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

  - [x] 2.2 Implement button variant styles
    - Add button styles in `/* 4. COMPONENT STYLES */` section of `src/styles.css`
    - Define `.btn` base + `.btn-primary`, `.btn-secondary`, `.btn-outline`, `.btn-ghost`, `.btn-icon` variants
    - Define `.btn-sm` (36px/12px), default (40px/16px), `.btn-lg` (48px/20px) sizes
    - Apply border-radius-md, hover color transitions (duration-fast), active scale(0.97), disabled opacity 0.5
    - _Requirements: 3.2, 3.6, 3.7, 3.8, 3.9_

  - [x] 2.3 Implement card, form input, table, and badge styles
    - Style `.metric-card`, `.panel`, `.item-card`, `.table-panel` with radius-lg, border neutral-200, shadow-sm
    - Style clickable cards with hover shadow-md + translateY(-2px) transition
    - Style form inputs: 40px height, 12px padding, neutral-300 border, radius-md, primary focus ring, neutral-400 placeholder, disabled state
    - Style `.badge` with 4px 10px padding, 999px radius, 12px font, weight 600
    - _Requirements: 3.1, 3.3, 3.4, 3.5, 3.8_

  - [x] 2.4 Implement table design refinements
    - Style table headers: uppercase, font-size xs (12px), neutral-400 text, 1px bottom border neutral-200
    - Apply alternating row colors for tables with >5 rows (transparent odd, neutral-50 even)
    - Add hover state: neutral-100 background with 150ms ease transition
    - Right-align numeric columns, left-align text columns
    - Style sort indicator icons (up, down, neutral bi-directional)
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6, 16.7_

- [x] 3. Shared Reusable Components
  - [x] 3.1 Create EmptyState component
    - Create `src/components/EmptyState.tsx` with props: icon, heading, description, actionLabel, onAction
    - Apply CSS class `.empty-state`: centered, 48px vertical padding, 24px horizontal padding, min-height 240px
    - Space elements: 16px icon→heading, 8px heading→description, 24px description→button
    - Heading: font-size lg (18px), weight 600; description: font-size base (14px), neutral-500
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [x] 3.2 Create ErrorState component
    - Create `src/components/ErrorState.tsx` with props: heading, description, onRetry
    - Use AlertCircle icon (48px) in danger color; heading in danger color; description in neutral-600
    - Apply CSS class `.error-state`: centered, 48px vertical padding, min-height 240px
    - Space elements: 16px icon→heading, 8px heading→description, 24px description→retry button
    - _Requirements: 7.1, 7.3, 7.4, 7.5_

  - [x] 3.3 Create SkeletonLoader component
    - Create `src/components/SkeletonLoader.tsx` with variant prop: text, card, table-row, chart
    - Support count and columns props for repeated skeleton elements
    - Define `.skeleton-pulse` keyframe: neutral-100 ↔ neutral-200 over 1.5s ease-in-out infinite
    - Ensure skeleton-card matches metric card grid layout; skeleton-chart has min-height 200px
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 3.4 Create Breadcrumbs component
    - Create `src/components/Breadcrumbs.tsx` using `useLocation` to parse path segments
    - Display "/" separator between levels, max 4 levels with intermediate "..." truncation
    - Add aria-label="Breadcrumb" for accessibility
    - _Requirements: 8.5_

  - [x] 3.5 Create SidebarGroup component
    - Create `src/components/SidebarGroup.tsx` with props: label, items (NavItem[])
    - Render group label: uppercase, font-size xs, weight 600, neutral-500
    - Render NavLink items with icon + label, active/hover state classes
    - _Requirements: 8.2_

  - [x] 3.6 Create MobileNav component
    - Create `src/components/MobileNav.tsx` with hamburger toggle, backdrop, and animated drawer
    - Use Framer Motion for drawer slide-in (x: -280→0) and backdrop fade
    - Toggle button with aria-label; backdrop click or toggle closes drawer
    - _Requirements: 8.6, 8.7_

- [x] 4. Checkpoint — Foundation and shared components
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Navigation Refinement
  - [x] 5.1 Refactor BusinessAppShell sidebar with grouped navigation
    - Update `src/panels/business/BusinessAppShell.tsx` to use `SidebarGroup` component
    - Organize into groups: Analytics, Customers, Management, Settings
    - Apply active state: 3px left border primary + primary-subtle background
    - Apply hover state: neutral-100 background with duration-fast transition
    - Ensure keyboard focusability with matching visual indicator
    - _Requirements: 8.1, 8.2, 8.4, 8.8_

  - [x] 5.2 Refactor AdminAppShell sidebar with grouped navigation
    - Update `src/panels/admin/AdminAppShell.tsx` to use `SidebarGroup` component
    - Organize into groups: Overview, Users & Access, ML Platform, Infrastructure, Audit
    - Apply active state: primary background + white text
    - Apply hover state: neutral-800 background with duration-fast transition
    - Ensure `.admin-shell` class wraps the shell for dark theme tokens
    - _Requirements: 8.3, 8.4, 8.8_

  - [x] 5.3 Integrate Breadcrumbs in topbar and add responsive sidebar collapse
    - Add `Breadcrumbs` component to both AppShell topbars
    - Add `MobileNav` integration: hide sidebar below 980px, show hamburger toggle in topbar
    - Ensure sidebar animates as overlay with backdrop on mobile
    - _Requirements: 8.5, 8.6, 8.7_

- [x] 6. Dashboard Layouts
  - [x] 6.1 Implement Business Dashboard KPI cards and section layout
    - Update `src/panels/business/pages/BusinessDashboard.tsx` with responsive KPI grid (4-col > 980px, 2-col 620–980px, 1-col < 620px)
    - Implement metric cards with label, value, and trend indicator (arrow + color-coded percentage)
    - Positive trend: success color + up arrow; negative: danger + down arrow; neutral: neutral-500, no arrow
    - Group charts/tables in labeled sections with 18px heading, weight 600, 32px spacing
    - Integrate SkeletonLoader for loading states (card + table-row + chart variants)
    - Integrate EmptyState and ErrorState for empty/error scenarios
    - _Requirements: 4.1, 4.2, 4.3, 4.5, 4.6, 4.7, 5.1, 5.2, 5.3, 5.6, 6.1_

  - [x] 6.2 Implement Admin Dashboard with dark-theme KPI cards
    - Update `src/panels/admin/pages/AdminDashboard.tsx` with responsive KPI grid matching business pattern
    - Implement admin metric cards with icon container (48px, rounded-xl, tinted bg) + label + value
    - Integrate SkeletonLoader and ErrorState for loading/error states
    - Ensure all cards consume dark-theme token values via `.admin-shell` inheritance
    - _Requirements: 4.4, 5.1, 5.2, 7.1_

  - [x] 6.3 Implement chart styling refinements
    - Update Recharts configurations across business dashboard pages
    - Apply design token colors for data series (primary, success, warning, danger, neutral-400, neutral-600)
    - Style chart containers: 16px padding, radius-lg corners
    - Style axis labels: 12px font, neutral-500 color; grid lines in neutral-200
    - Style tooltips: white bg, shadow-sm, radius-md, 12px padding, font-size sm
    - Style legends: 12px font, neutral-600 color, positioned below chart
    - Display EmptyState when chart data is empty/null
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

- [x] 7. Checkpoint — Navigation and dashboards complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Marketing Pages Polish
  - [x] 8.1 Redesign Landing page
    - Update `src/pages/LandingPage.tsx` with hero section (headline, sub-headline, dual CTAs, gradient overlay with 7:1 contrast)
    - Add social proof stats bar with 3+ metrics between hero and features
    - Add features grid (3 or 6 cards with Lucide icon, heading, description)
    - Add final CTA section with dark background and signup button
    - Ensure hero is above-fold on 768px+ viewports (min-height: calc(100vh - 64px))
    - Ensure CLS below 0.1 with explicit dimensions
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

  - [x] 8.2 Redesign Pricing page
    - Update `src/pages/PricingPage.tsx` with 3-column plan grid (equal height, 24px padding/gap)
    - Highlight recommended plan: primary border, badge, shadow-lg, primary button variant
    - Each card: name, price, billing period, description, feature list (3–10 items with check icon), CTA button
    - Non-recommended plans use outline button variant
    - Stack vertically below 980px, recommended plan first (order: -1)
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [x] 8.3 Redesign About and Contact pages
    - Update `src/pages/AboutPage.tsx`: hero + mission statement + 3-column values grid + tech stack section
    - Update `src/pages/ContactPage.tsx`: 2-column layout (info left, form right), stacking below 980px
    - Implement contact form validation: name (1–100 chars), email (standard format), message (1–2000 chars)
    - Show inline validation errors below invalid fields on blur/submit
    - Show success confirmation on successful submit; show error message on failure, preserving values
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

  - [x] 8.4 Implement sticky marketing navigation bar
    - Add sticky nav with blur backdrop to all marketing pages (shared layout or per-page)
    - Display brand logo, page links (Home, About, Pricing, Contact), and Sign In CTA button
    - Collapse to hamburger drawer below 620px
    - _Requirements: 12.6, 14.5_

- [x] 9. Auth Pages Polish
  - [x] 9.1 Redesign authentication pages
    - Update `src/pages/SignInPage.tsx`, `SignUpPage.tsx`, `VerifyEmailPage.tsx`, `PasswordResetRequestPage.tsx`, `PasswordResetConfirmPage.tsx`
    - Implement centered card layout (max-width 420px) on full-height gradient background
    - Card: brand logo, heading, form fields with labels, submit button, footer links, 24px vertical spacing between groups
    - Style form focus ring: 2px primary, 2px offset
    - _Requirements: 13.1, 13.2, 13.5_

  - [x] 9.2 Implement auth form validation and submission states
    - Add inline validation on blur + submit: error below field in danger color, font-size sm, within 100ms
    - Add loading state: disable button + show spinner inside button during submission
    - Add 15-second timeout: re-enable button, show timeout error message
    - Add auth failure handling: inline error above submit button, preserve values except password (clear password field)
    - Handle duplicate email on signup with generic security-safe error message
    - _Requirements: 13.3, 13.4, 13.6, 13.7_

- [x] 10. Checkpoint — Pages complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Responsive Design and Accessibility
  - [x] 11.1 Implement responsive media queries for 980px and 620px breakpoints
    - Add `/* 12. RESPONSIVE — 980px breakpoint */` section: sidebar collapse, 2-col grids, reduced spacing
    - Add `/* 13. RESPONSIVE — 620px breakpoint */` section: 1-col grids, 16px page padding, 20px section spacing
    - Reflow metric grids, card grids, feature grids, pricing grid at breakpoints
    - Ensure marketing nav collapses to hamburger at 620px
    - Ensure 44px minimum touch targets on viewports below 980px
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5_

  - [x] 11.2 Implement overflow prevention and prefers-reduced-motion
    - Add `min-width: 0` on grid children, `max-width: 100%` on images, `overflow-x: auto` on table containers
    - Ensure no element exceeds 100% viewport width at any breakpoint
    - Add `/* 14. ACCESSIBILITY — prefers-reduced-motion */` section with `animation-duration: 0ms; transition-duration: 0ms` for all elements
    - _Requirements: 14.6, 9.7_

  - [x] 11.3 Implement micro-animation and transition system
    - Add `/* 11. ANIMATIONS & TRANSITIONS */` section in `src/styles.css`
    - Apply `transition: background-color, border-color` with duration-fast to all interactive elements
    - Apply card hover transitions (translateY -2px + shadow-md over duration-normal)
    - Ensure Framer Motion page transitions (fade + 8px slide, 200ms ease-out) work in AppShells
    - Ensure modal/dropdown open (scale 0.95→1, 150ms) and close (scale 1→0.95, 150ms) animations
    - Ensure toast slides from top-right (300ms ease-out)
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

- [x] 12. Final Checkpoint — All features complete
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All CSS changes target the single `src/styles.css` file organized into clearly commented sections
- New React components go in `src/components/` as shared utilities consumed by both panels
- Existing page components in `src/panels/` and `src/pages/` are updated in-place
- No new dependencies are introduced — leverages React 18, TypeScript, Framer Motion, Lucide React, Recharts, and Zustand
- Tasks are ordered so each step builds on the previous: tokens → base styles → components → navigation → dashboards → pages → responsive
- Responsive behavior is layered last to avoid re-work as component styles are finalized
- The design has no Correctness Properties section, so property-based tests are omitted in favor of unit tests and visual regression testing

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "2.4"] },
    { "id": 3, "tasks": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6"] },
    { "id": 4, "tasks": ["5.1", "5.2"] },
    { "id": 5, "tasks": ["5.3"] },
    { "id": 6, "tasks": ["6.1", "6.2"] },
    { "id": 7, "tasks": ["6.3"] },
    { "id": 8, "tasks": ["8.1", "8.2", "8.3"] },
    { "id": 9, "tasks": ["8.4"] },
    { "id": 10, "tasks": ["9.1"] },
    { "id": 11, "tasks": ["9.2"] },
    { "id": 12, "tasks": ["11.1", "11.2", "11.3"] }
  ]
}
```
