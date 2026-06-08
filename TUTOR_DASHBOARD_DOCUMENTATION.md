# Tutor Dashboard Documentation (HTML + CSS)

This document explains what each line/section is doing in:
- `templates/tutor_dashboard.html`
- `static/css/tutor-dashboard.css`

---

## 1) `templates/tutor_dashboard.html` (structure)

```html
<!DOCTYPE html>
<html lang="en">
```
- `<!DOCTYPE html>`: tells the browser this is modern HTML.
- `<html lang="en">`: sets the page language for accessibility/search.

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ZitConnect - Tutor Dashboard</title>
  <link rel="stylesheet" href="/static/css/tutor-dashboard.css">
</head>
```
- `<meta charset="UTF-8">`: ensures correct character encoding.
- `<meta name="viewport" ...>`: makes layout responsive on mobile.
- `<title>`: browser tab title.
- `<link>`: loads the CSS file that styles the dashboard.

```html
<body>
  <div class="Dashboard">
```
- `<body>`: visible page content.
- `<div class="Dashboard">`: main wrapper. CSS uses it as a 2-column grid (left sidebar + right content).

### Left sidebar
```html
<div class="left">
  <div class="Header">
    <div class="logo-circle"></div>
    <h1>ZitConnect</h1>
  </div>
```
- `.left`: sidebar panel.
- `.Header`: top area of sidebar (logo + title).
- `.logo-circle`: empty div; CSS draws the circle + “zc” via `::after`.

```html
<div class="menu-item"> ... </div>
```
- Each `.menu-item` is a clickable-looking row.
- `<span class="menu-icon">...</span>` displays the emoji icon.
- The CSS aligns icon + text and adds hover background.

Close sidebar:
```html
</div>
```

### Right content
```html
<div class="right">
  <div class="Welcome_part">
    <h2>Welcome, User</h2>
  </div>
```
- `.right`: right panel background + padding.
- `.Welcome_part`: the welcome text area.
  - CSS keeps spacing but removes the grey boxed background (transparent) so the background surrounds main content.

Cards section:
```html
<div class="cards-container">
  <div class="card"> ... </div>
  ...
</div>
```
- `.cards-container`: flex row so cards appear on one line.
- Each `.card` has a fixed width and white background like “Total Earnings”.

Bottom table/card:
```html
<div class="bottom">
  <div class="Container"> ... </div>
  <div class="session-row"> ... </div>
</div>
```
- `.bottom`: the white rounded container holding the table-like UI.
- `.Container`: header row (Student/Course/Date/Type/Actions).
- `.session-row`: one data row.
- `.action-buttons`: wraps buttons aligned in one line.

Close all wrappers and document:
```html
</div> ... </div>
</body>
</html>
```

---

## 2) `static/css/tutor-dashboard.css` (styling)

### Global reset
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
```
- Applies to all elements:
  - removes default spacing
  - `box-sizing: border-box` makes widths/padding behave predictably.

```css
body {
    font-family: ...;
    background: #f0f2f5;
}
```
- Sets the default font.
- Sets the page background color.

---

### Dashboard layout (2 columns)
```css
.Dashboard {
    display: grid;
    grid-template-columns: 260px 1fr;
    min-height: 100vh;
}
```
- `.Dashboard` uses CSS Grid.
- First column is 260px (sidebar).
- Second column takes remaining width.
- `min-height: 100vh` ensures full viewport height.

Sidebar styling:
```css
.left {
    background: #1a3a5c;
    color: white;
    padding: 25px 0;
}
```
- Dark blue sidebar.
- White text.
- Vertical padding.

Header row in sidebar:
```css
.Header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 20px 20px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    margin-bottom: 10px;
}
```
- `.Header` is flex so logo circle and title align horizontally.
- `gap: 10px` adds spacing.
- Bottom border separates header from menu.

Logo circle:
```css
.logo-circle {
    width: 50px;
    height: 50px;
    background: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}
```
- Creates the circular logo background.
- Uses flex to center any pseudo-content.

```css
.logo-circle::after {
    content: "zc";
    color: #1a3a5c;
    font-weight: 800;
    font-size: 18px;
}
```
- Adds text “zc” inside the circle without modifying HTML.

Menu item rows:
```css
.menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 20px;
    cursor: pointer;
    transition: background 0.3s;
    font-size: 16px;
    color: white;
}
```
- Flex row aligning icon + label.
- Hover-ready with `transition`.

```css
.menu-item:hover {
    background: rgba(255, 255, 255, 0.15);
}
```
- Hover highlight effect.

```css
.menu-icon {
    font-size: 18px;
    width: 25px;
}
```
- Ensures emoji column width and size.

---

### Right panel
```css
.right {
    background: #f5f7fa;
    padding: 20px;
    min-height: calc(100vh - 0px);
}
```
- Light grey right background.
- Padding around content.
- `min-height` keeps panel tall.

Welcome box (no grey box):
```css
.Welcome_part {
    background: transparent;
    padding: 18px 20px;
    border-radius: 12px;
    margin-bottom: 18px;
}
```
- `background: transparent` removes the boxed grey section.
- Keeps padding + radius so spacing remains consistent.

---

### Bottom container (white “box”)

Important: There are BOTH `.right .bottom` and `.bottom` rules. Final visual result is:
- `.bottom` defines the white container (the main one).

```css
.bottom {
    background: #ffffff;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: none;
    margin-top: 18px;
    padding: 0;
    border: 1px solid #e5e7eb;
}
```
- White container like your cards.
- Rounded corners.
- `overflow: hidden` ensures rounded corners clip child rows.
- Light border.

Also defined to ensure container inside right panel is white:
```css
.right .bottom {
    background: #ffffff;
    border: none;
}
```
- This is an override-style selector.

---

### Table header row
```css
.Container {
    display: grid;
    grid-template-columns: 2fr 2fr 1.5fr 1.5fr 2fr;
    background: #ffffff;
    padding: 14px 20px;
    border-bottom: 1px solid #e0e0e0;
}
```
- Uses grid to create 5 aligned “columns”.
- `2fr` / `1.5fr` control column width proportions.
- Header row has white background and a subtle separator line.

```css
.Container h3 {
    color: #333;
    font-size: 14px;
    font-weight: 600;
}
```
- Typography for header labels.

---

### Session data row (“candy bar” pill)
```css
.session-row {
    display: grid;
    grid-template-columns: 2fr 2fr 1.5fr 1.5fr 2fr;
    padding: 14px 20px;
    border-bottom: 1px solid #e0e0e0;
    align-items: center;
    border-radius: 999px;
}
```
- Same 5-column grid so values align with headers.
- The key “candy bar” effect is `border-radius: 999px`.
- `align-items: center` vertically centers text.

Row text:
```css
.session-row span {
    color: #333;
    font-size: 14px;
}
```
- Sets consistent row typography.

Ensure row background stays white:
```css
.right .session-row {
    background: #ffffff;
}
```

---

### Action buttons
```css
.action-buttons {
    display: flex;
    gap: 10px;
}
```
- Keeps buttons on the same line with spacing.

Accept button:
```css
.accept-btn {
    background: #28a745;
    color: white;
    border: none;
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
}
.accept-btn:hover {
    background: #1e7e34;
}
```
- Green style + hover darkening.

Decline button:
```css
.decline-btn {
    background: #dc3545;
    color: white;
    border: none;
    padding: 6px 14px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
}
.decline-btn:hover {
    background: #bd2130;
}
```
- Red style + hover darkening.

---

### Mobile responsiveness
```css
@media (max-width: 768px) {
    .Dashboard { grid-template-columns: 200px 1fr; }
    .cards-container { flex-direction: column; }
    .Container, .session-row {
        grid-template-columns: 1fr;
        gap: 8px;
        text-align: center;
    }
}
```
- Sidebar shrinks a bit.
- Cards stack vertically.
- Table header + row collapse to a single column, stacked layout.

---

## Notes / Key “Why this looks like it does”
- The “grey welcome box” is removed by making `.Welcome_part` transparent.
- The “bottom” is a dedicated white card/box via `.bottom { background: #ffffff; border-radius: 14px; }`.
- The “long candy bar line” is mainly controlled by `.session-row { border-radius: 999px; }` and the grid column setup.

