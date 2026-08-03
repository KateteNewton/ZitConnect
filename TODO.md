# TODO: Make all admin pages mobile responsive

## Goal
Bring all 5 admin pages to the same mobile-responsive standard as `admin_dashboard_main.html` (which already has a hamburger toggle, slide-out sidebar, overlay, and breakpoints).

## Status Tracker
- [x] Analyze admin pages (only admin_dashboard_main.html is fully responsive)
- [x] Add responsive styles + hamburger toggle + JS to `admin_users.html`
- [x] Add responsive styles + hamburger toggle + JS to `admin_courses.html`
- [x] Add responsive styles + hamburger toggle + JS to `admin_verification.html`
- [x] Add responsive styles + hamburger toggle + JS to `admin_profile.html`
- [x] Verify the app runs and pages render responsively

## Pattern to replicate (from admin_dashboard_main.html / manage_courses.html)
1. Responsive `<style>` block in `<head>`:
   - `.mobile-menu-toggle` (fixed hamburger button)
   - `.sidebar-overlay`
   - `@media (max-width: 992px)` tablet adjustments
   - `@media (max-width: 768px)` sidebar becomes slide-out panel
   - `@media (max-width: 480px)` small phones
   - Touch-friendly target sizing
2. Mobile toggle button + overlay markup after `<body>`
3. Add `id="sidebar"` to `.left` sidebar element
4. Mobile menu toggle JavaScript before `</body>`
