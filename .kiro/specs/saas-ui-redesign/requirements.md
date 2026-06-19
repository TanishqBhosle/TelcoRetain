# Requirements Document

## Introduction

TelcoRetain is a customer churn prediction and retention management platform. The current frontend was rapidly prototyped and exhibits visual patterns commonly associated with AI-generated UIs — inconsistent spacing, flat visual hierarchy, generic component styling, and lack of micro-interactions that signal craftsmanship. This redesign transforms the UI into a polished, professional SaaS product by establishing a design system with consistent tokens, refining typography and color usage, introducing professional state patterns (loading, empty, error), and elevating the marketing pages to conversion-focused experiences. The redesign retains the existing technology stack (React 18, TypeScript, Vite, plain CSS with custom properties, Framer Motion, Recharts, Lucide React) and does not introduce any component libraries.

## Glossary

- **Design_System**: A set of CSS custom properties (tokens) and reusable class-based component styles that enforce visual consistency across the application
- **Business_Panel**: The light-themed authenticated application interface used by Retention Managers, Marketing Managers, Business Analysts, Customer Support Executives, and Executive Viewers
- **Admin_Panel**: The dark-themed authenticated application interface used by Super Admins and Admins for system configuration and monitoring
- **Marketing_Pages**: The public-facing pages (Landing, About, Pricing, Contact) used to attract and convert visitors into users
- **Auth_Pages**: The pages handling authentication flows (Sign In, Sign Up, Verify Email, Password Reset)
- **AppShell**: The sidebar + topbar layout wrapper that contains navigation and page content for authenticated panels
- **Design_Token**: A CSS custom property that stores a single design decision (color, spacing, radius, shadow, font size) for reuse
- **Visual_Hierarchy**: The arrangement of elements to show importance through size, weight, color contrast, and spacing
- **Micro_Animation**: A subtle motion effect (under 400ms) applied to interactive elements to provide feedback and polish
- **Empty_State**: A UI pattern displayed when a list, table, or section has no data to show
- **Loading_State**: A UI pattern displayed while asynchronous data is being fetched
- **Error_State**: A UI pattern displayed when a data fetch or operation fails
- **Skeleton_Loader**: A placeholder UI element that mimics content layout using animated gray blocks while data loads
- **Breakpoint**: A screen width value at which the layout adapts for different device sizes

## Requirements

### Requirement 1: Design Token System

**User Story:** As a developer, I want a centralized design token system in CSS custom properties, so that all components share consistent spacing, colors, radii, and typography values.

#### Acceptance Criteria

1. THE Design_System SHALL define a color palette with at least primary, primary-hover, primary-subtle, neutral-50 through neutral-900, success, warning, danger, and surface token groups in CSS custom properties on the :root selector
2. THE Design_System SHALL define a spacing scale with tokens from 4px to 64px in consistent increments (4, 8, 12, 16, 20, 24, 32, 40, 48, 64)
3. THE Design_System SHALL define a typography scale with font-size tokens for xs (12px), sm (13px), base (14px), md (15px), lg (18px), xl (20px), 2xl (24px), 3xl (32px), and 4xl (40px)
4. THE Design_System SHALL define border-radius tokens for sm (4px), md (6px), lg (8px), xl (12px), and 2xl (16px)
5. THE Design_System SHALL define box-shadow tokens for sm, md, lg, and xl elevation levels, where each token specifies offset-x, offset-y, blur-radius, and rgba color values forming a progressively increasing elevation (sm having the smallest blur-radius and offset, xl having the largest)
6. THE Design_System SHALL define transition tokens for duration-fast (150ms), duration-normal (200ms), and duration-slow (300ms)
7. WHEN the Admin_Panel is rendered, THE Design_System SHALL apply a dark-theme token override that redefines at minimum the color palette tokens (primary, neutral, surface, success, warning, and danger groups) with dark-appropriate values, scoped to a dedicated admin shell container element using a CSS class selector so that tokens outside the container remain unchanged

### Requirement 2: Typography and Visual Hierarchy

**User Story:** As a user, I want clear visual hierarchy on every page, so that I can quickly scan and understand information importance.

#### Acceptance Criteria

1. THE Design_System SHALL apply font-weight 700 or 800 to page-level headings (h1) and font-weight 600 to section headings (h2) to establish clear hierarchy
2. THE Design_System SHALL use a line-height of 1.2 for headings and 1.5 for body text to improve readability
3. THE Design_System SHALL apply color contrast of at least 4.5:1 between text and background for all body text elements
4. THE Design_System SHALL use secondary text color (neutral-500) for labels, captions, and metadata, maintaining a minimum contrast ratio of 3:1 against the background to separate primary from secondary information while remaining legible
5. IF a heading has a computed font-size greater than 24px, THEN THE Design_System SHALL apply letter-spacing of -0.01em for optical tightness
6. THE Design_System SHALL define a font-size scale where h1 is at least 30px, h2 is at least 24px, h3 is at least 20px, and body text is at least 16px, with each heading level being at least 4px larger than the next lower level

### Requirement 3: Component Design Language

**User Story:** As a user, I want consistent component styling throughout the application, so that the interface feels cohesive and professional.

#### Acceptance Criteria

1. THE Design_System SHALL style all card-type components (metric-card, panel, item-card, table-panel) with border-radius using the lg token, border color using neutral-200, and box-shadow using the sm shadow token
2. THE Design_System SHALL style all button variants (primary, secondary, outline, ghost, icon) with height (36px small, 40px default, 48px large), horizontal padding (12px small, 16px default, 20px large), border-radius using the md token, and a minimum width of 36px for icon-only buttons
3. THE Design_System SHALL style all form inputs with consistent height (40px), padding (0 12px), border (1px solid neutral-300), border-radius using the md token, focus ring (2px primary color offset by 2px), and placeholder color using neutral-400
4. THE Design_System SHALL style all status badges (pills) with consistent padding (4px 10px), border-radius (999px), font-size (12px), and font-weight (600)
5. WHEN a clickable card is hovered, THE Design_System SHALL apply the md shadow token to indicate interactivity
6. WHEN a button is hovered, THE Design_System SHALL apply a background-color transition using the duration-fast token
7. WHEN a button is pressed, THE Design_System SHALL apply a scale transform of 0.97 for tactile feedback
8. WHILE a button or form input is in the disabled state, THE Design_System SHALL reduce the element opacity to 0.5 and prevent pointer events
9. WHEN a button is hovered, THE Design_System SHALL darken the background-color by applying the corresponding hover token (e.g., primary-hover for primary variant) and display a pointer cursor

### Requirement 4: Dashboard and Data Layout

**User Story:** As a Retention Manager, I want dashboard layouts that present metrics and charts with clear grouping and emphasis, so that I can make data-driven decisions at a glance.

#### Acceptance Criteria

1. THE Business_Panel dashboard SHALL display KPI metric cards in a responsive grid that shows 4 cards per row on viewports above 980px, 2 cards per row on viewports between 620px and 980px, and 1 card per row on viewports below 620px
2. THE Business_Panel dashboard metric cards SHALL display the metric label, current value, and a trend indicator showing percentage change with a directional arrow icon and color coding as defined in criteria 5, 6, and 7
3. THE Business_Panel dashboard SHALL group related charts and tables in labeled sections where each section heading uses font-size lg (18px), font-weight 600, and is positioned above its content group with consistent section spacing of 32px between groups
4. THE Admin_Panel dashboard SHALL display system KPIs in a 4-column grid on viewports above 980px with icon, label, and value per card, reflowing to 2 columns on viewports between 620px and 980px, and 1 column below 620px
5. WHEN a metric card has a positive trend (percentage change greater than 0%), THE Business_Panel SHALL display the trend value in success color with an upward arrow icon
6. WHEN a metric card has a negative trend (percentage change less than 0%), THE Business_Panel SHALL display the trend value in danger color with a downward arrow icon
7. WHEN a metric card has a neutral trend (percentage change equal to 0%), THE Business_Panel SHALL display the trend value in muted color (neutral-500) with no directional arrow icon

### Requirement 5: Loading States

**User Story:** As a user, I want professional loading indicators while data fetches, so that I know the system is working and the interface does not flash empty content.

#### Acceptance Criteria

1. WHILE data is loading for a table, THE AppShell SHALL display 5 skeleton loader rows matching the table column count and column widths with pulse animation
2. WHILE data is loading for metric cards, THE AppShell SHALL display skeleton loader cards in the same grid layout and dimensions as the metric cards with pulse animation
3. WHILE data is loading for chart sections, THE AppShell SHALL display a skeleton loader with a minimum height of 200px matching the chart container width with pulse animation
4. THE Skeleton_Loader pulse animation SHALL use a CSS keyframe that transitions background-color between neutral-100 and neutral-200 over 1.5 seconds with ease-in-out timing and infinite repetition
5. WHILE a page is loading, THE AppShell SHALL render skeleton loaders synchronously on initial mount so that no frame paints without placeholder content, maintaining a Cumulative Layout Shift below 0.1
6. WHEN data loading completes for a section, THE AppShell SHALL replace the skeleton loader with the actual content using a fade transition over 150ms

### Requirement 6: Empty States

**User Story:** As a user, I want informative empty states with clear messaging and actions, so that I understand why there is no data and what to do next.

#### Acceptance Criteria

1. WHEN a table or list has no data, THE Business_Panel SHALL display an empty state with a Lucide icon sized at 48px, a heading (max 60 characters), a description (max 120 characters), and a primary action button that navigates to the relevant creation or import flow for that data type
2. WHEN search or filter results return zero items, THE Business_Panel SHALL display an empty state with a search-themed Lucide icon, a heading indicating no results match, a description referencing the active filter criteria, and a "Clear Filters" button that resets all active filters to their default values
3. THE Empty_State component SHALL center content vertically and horizontally within its container with 48px vertical padding and 24px horizontal padding, and a minimum height of 240px
4. THE Empty_State heading SHALL use font-size lg (18px) and font-weight 600
5. THE Empty_State description SHALL use font-size base (14px) in muted color (neutral-500)
6. THE Empty_State component SHALL space internal elements with 16px between the icon and heading, 8px between heading and description, and 24px between description and action button

### Requirement 7: Error States

**User Story:** As a user, I want clear error states that explain what went wrong and offer recovery actions, so that I can resolve issues without confusion.

#### Acceptance Criteria

1. IF a data fetch fails, THEN THE AppShell SHALL display an error state with a Lucide AlertCircle icon sized at 48px in danger color, a human-readable error heading, a descriptive body message, and a retry button
2. IF a form submission fails, THEN THE AppShell SHALL display an inline error message below the form in danger color with font-size sm, preserving all user-entered field values
3. THE Error_State component SHALL use danger color for the icon and heading, neutral body text (neutral-600) for the description, and center content vertically and horizontally with 48px vertical padding and a minimum height of 240px
4. WHEN the retry button in an error state is clicked, THE AppShell SHALL re-attempt the failed operation and display the loading state
5. THE Error_State component SHALL space internal elements with 16px between the icon and heading, 8px between heading and description, and 24px between description and retry button

### Requirement 8: Navigation and Sidebar Refinement

**User Story:** As a user, I want refined navigation that clearly shows where I am and provides smooth transitions between sections, so that I can orient myself in the application.

#### Acceptance Criteria

1. THE Business_Panel sidebar SHALL display navigation items with an active state indicator that uses a left border accent (3px primary color) and a background color of primary-subtle token
2. THE Business_Panel sidebar SHALL group navigation items into labeled sections (e.g., "Analytics", "Management", "Settings") with section labels in uppercase, font-size xs (12px), font-weight 600, and neutral-500 color
3. THE Admin_Panel sidebar SHALL display navigation items with an active state that uses primary background color and white text
4. WHEN a navigation item is hovered, THE AppShell sidebar SHALL transition the item background color to neutral-100 (Business_Panel) or neutral-800 (Admin_Panel) using duration-fast token
5. THE AppShell topbar SHALL display a breadcrumb trail showing the current location within the application hierarchy, using a "/" separator between levels, displaying a maximum of 4 levels with intermediate levels truncated to "..." when exceeded
6. WHEN the viewport width is below 980px, THE AppShell sidebar SHALL collapse to a hidden off-screen state and display a hamburger toggle button in the topbar
7. WHEN the hamburger toggle button is clicked while the sidebar is collapsed, THE AppShell sidebar SHALL animate into view as an overlay with a backdrop, and WHEN the toggle is clicked again or the backdrop is clicked, THE AppShell sidebar SHALL animate out of view
8. THE AppShell sidebar navigation items SHALL be focusable via keyboard and SHALL display the same visual indicator on focus as on hover

### Requirement 9: Micro-Animations and Interactions

**User Story:** As a user, I want subtle animations on interactive elements, so that the interface feels responsive and polished.

#### Acceptance Criteria

1. WHEN a page route changes, THE AppShell SHALL animate the page content in with a fade and 8px upward slide over 200ms with ease-out easing
2. WHEN a modal or dropdown opens, THE AppShell SHALL animate the element in with opacity from 0 to 1 and scale from 0.95 to 1 over 150ms with ease-out easing
3. WHEN a toast notification appears, THE AppShell SHALL animate the toast sliding in from the top-right with a 300ms ease-out transition
4. THE Design_System SHALL apply transition on background-color and border-color properties to all interactive elements (buttons, nav items, inputs) using duration-fast token with ease-in-out easing
5. WHEN a card is hovered in a grid layout, THE Design_System SHALL apply a translateY(-2px) transform and shadow-md token over duration-normal
6. WHEN a modal or dropdown closes, THE AppShell SHALL animate the element out with opacity from 1 to 0 and scale from 1 to 0.95 over 150ms with ease-in easing
7. IF the user has enabled prefers-reduced-motion in their operating system, THEN THE Design_System SHALL disable all transition durations and animations by setting duration to 0ms for all animated elements

### Requirement 10: Marketing Pages — Landing Page

**User Story:** As a visitor, I want a compelling landing page that clearly communicates TelcoRetain's value proposition, so that I understand the product and am motivated to sign up.

#### Acceptance Criteria

1. THE Marketing_Pages landing page SHALL display a hero section with a headline (max 10 words), sub-headline (max 25 words), primary CTA button navigating to /signup, and secondary CTA button navigating to /pricing, all visible without scrolling on viewports with height 768px or greater
2. THE Marketing_Pages landing page hero section SHALL use a gradient overlay on a background with minimum text contrast of 7:1
3. THE Marketing_Pages landing page SHALL display a social proof stats bar with at least 3 quantified metrics (e.g., customers served, churn reduction percentage) positioned between hero and features sections
4. THE Marketing_Pages landing page SHALL display a features grid with 3 or 6 feature cards, each containing a Lucide icon, a heading (max 6 words), and a description (max 20 words)
5. THE Marketing_Pages landing page SHALL display a final CTA section with a dark background, heading, description, and primary action button navigating to /signup
6. THE Marketing_Pages landing page SHALL load with no visible layout shift (CLS below 0.1)

### Requirement 11: Marketing Pages — Pricing Page

**User Story:** As a visitor, I want a clear pricing page that compares plan features, so that I can choose the right tier for my organization.

#### Acceptance Criteria

1. THE Marketing_Pages pricing page SHALL display exactly 3 plan cards in a 3-column grid with equal heights, 24px internal padding, and 24px gap between columns
2. THE Marketing_Pages pricing page SHALL visually emphasize the recommended plan with a highlighted border using the primary color, a badge label above or inside the card, and the lg elevation shadow token
3. THE Marketing_Pages pricing page SHALL display each plan with: name, price (currency symbol followed by numeric value with up to 2 decimal places), billing period (e.g., "/month" or "/year"), description (maximum 2 lines), feature list of 3 to 10 items each preceded by a check icon, and a CTA button
4. THE Marketing_Pages pricing page CTA buttons SHALL differentiate between primary (recommended plan) and outline (other plans) variants as defined in the Design_System button styles
5. WHEN the viewport is below 980px, THE Marketing_Pages pricing page SHALL stack plan cards vertically with the recommended plan displayed first and 16px gap between stacked cards

### Requirement 12: Marketing Pages — About and Contact

**User Story:** As a visitor, I want professional About and Contact pages that build trust, so that I feel confident in the product and company.

#### Acceptance Criteria

1. THE Marketing_Pages about page SHALL display a hero section with a page heading and subheading, a mission statement paragraph, company values in a card grid of 3 columns on viewports above 980px and 1 column below, and a technology stack section listing tools used
2. THE Marketing_Pages contact page SHALL display a two-column layout with contact information (email address, phone number, and office address) on the left and a contact form on the right, stacking to a single column on viewports below 980px
3. IF the contact form is submitted with any required field (name, email, message) empty or invalid, THEN THE Marketing_Pages contact page SHALL prevent submission and display an inline validation error below each invalid field, where name must be between 1 and 100 characters, email must match a standard email format, and message must be between 1 and 2000 characters
4. WHEN the contact form is submitted successfully, THE Marketing_Pages contact page SHALL display a success confirmation message with a check icon and text indicating the message has been received
5. IF the contact form submission fails due to a network or server error, THEN THE Marketing_Pages contact page SHALL display an inline error message indicating the submission could not be completed and preserve all user-entered field values
6. THE Marketing_Pages navigation bar SHALL be sticky with a blur backdrop effect and display the brand logo, page links, and a sign-in CTA button

### Requirement 13: Auth Pages Polish

**User Story:** As a user, I want professional authentication pages with clear form layouts and feedback, so that signing in and signing up feels trustworthy and frictionless.

#### Acceptance Criteria

1. THE Auth_Pages SHALL display a centered card (max-width 420px) on a full-height background with a gradient overlay for each authentication flow: Sign In, Sign Up, Verify Email, and Password Reset
2. THE Auth_Pages card SHALL display the brand logo, page heading, form fields with labels, primary submit button, and footer links (e.g., "Don't have an account? Sign up") with consistent vertical spacing of 24px between form groups
3. WHEN the user submits the auth form or moves focus away from a required field that is empty or invalid, THE Auth_Pages SHALL display an error message directly below the field in danger color with font-size sm within 100ms of the triggering event
4. WHILE the auth form is submitting, THE Auth_Pages SHALL disable the submit button and display a loading spinner inside the button; IF the submission does not complete within 15 seconds, THEN THE Auth_Pages SHALL re-enable the submit button and display an error message indicating a timeout occurred
5. THE Auth_Pages form fields SHALL display a focus ring using the primary color with 2px width and 2px offset
6. IF authentication fails due to invalid credentials or a server error, THEN THE Auth_Pages SHALL display an inline error message above the submit button in danger color describing the failure reason, and SHALL preserve all user-entered field values except the password field which SHALL be cleared
7. WHEN the user submits a Sign Up form with an email address already registered, THEN THE Auth_Pages SHALL display an error message indicating the email is already in use without revealing whether an account exists for security purposes

### Requirement 14: Responsive Design

**User Story:** As a user on a tablet or mobile device, I want the application to adapt gracefully to smaller screens, so that I can use TelcoRetain on any device.

#### Acceptance Criteria

1. WHEN the viewport width is below 980px, THE AppShell SHALL collapse the sidebar and display a mobile navigation toggle in the topbar
2. WHEN the viewport width is below 980px, THE Design_System SHALL reflow multi-column grids (metric grids, card grids, feature grids) to two-column layouts, and to single-column layouts below 620px
3. WHEN the viewport width is below 620px, THE Design_System SHALL reduce page padding from 28px to 16px and reduce section spacing from 32px to 20px
4. THE Design_System SHALL ensure all interactive elements (buttons, nav items, form controls) maintain a minimum touch target of 44px width and 44px height on viewports below 980px
5. WHEN the viewport width is below 620px, THE Marketing_Pages navigation SHALL collapse into a hamburger menu with a slide-out drawer
6. THE Design_System SHALL prevent horizontal overflow on all viewports by ensuring no element exceeds 100% of the viewport width

### Requirement 15: Data Visualization Refinement

**User Story:** As a Retention Manager, I want polished chart designs that match the application design language, so that data visualizations feel integrated rather than like embedded third-party widgets.

#### Acceptance Criteria

1. THE Business_Panel charts SHALL use the design token color palette for data series colors, assigning series in this order: primary, success, warning, danger, neutral-400, and neutral-600 for up to 6 data series
2. THE Business_Panel charts SHALL display with consistent padding (16px) inside their container cards and rounded corners matching the card border-radius token (border-radius-lg)
3. THE Business_Panel charts SHALL display axis labels in font-size xs (12px), muted color (neutral-500), and with at most one horizontal grid line set rendered in neutral-200
4. THE Business_Panel charts SHALL display tooltips with a white background, box-shadow-sm token, border-radius-md token (6px), 12px padding, and font-size sm (13px) for content text
5. WHEN a chart receives an empty data array or a null/undefined data response, THE Business_Panel SHALL display the empty state component instead of rendering an empty chart area
6. THE Business_Panel charts SHALL display legends (when present) using font-size xs (12px), neutral-600 color, and position them below the chart with 8px spacing between legend items

### Requirement 16: Table Design Refinement

**User Story:** As a user viewing tabular data, I want polished tables that are easy to scan, so that I can find and compare information efficiently.

#### Acceptance Criteria

1. THE Design_System tables SHALL display header rows in uppercase at font-size xs (12px), using the neutral-400 text color, with a 1px solid bottom border in neutral-200
2. IF a table contains more than 5 rows, THEN THE Design_System SHALL apply alternating row background colors (transparent for odd rows and neutral-50 for even rows)
3. WHEN a user hovers over a table data row, THE Design_System SHALL change the row background to neutral-100 with a 150ms ease transition
4. THE Design_System tables SHALL right-align columns containing numeric values and left-align columns containing text values
5. WHILE a table column is sorted in ascending order, THE Design_System SHALL display an upward-pointing sort indicator icon to the right of that column header text
6. WHILE a table column is sorted in descending order, THE Design_System SHALL display a downward-pointing sort indicator icon to the right of that column header text
7. WHEN a sortable column is in its unsorted state, THE Design_System SHALL display a neutral bi-directional sort indicator icon to the right of that column header text
