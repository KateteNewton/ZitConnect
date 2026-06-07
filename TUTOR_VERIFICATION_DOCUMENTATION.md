# Tutor Verification Integration Documentation

## What was done
1. Added a **Tutor Verification page** using your provided HTML.
2. Moved the relevant CSS rules into an external stylesheet so the page can load CSS normally.
3. Updated Flask (`app.py`) so the verification page is accessible via a URL.
4. Adjusted the page styling to look more like the existing **student pages** in this repo by adding an additional CSS file.

---

## Files changed / created

### 1) `templates/tutor_Verification.html`
This file now contains the full Tutor Verification UI (HTML) including:
- A header (TopAppBar)
- A document upload area with drag-and-drop
- A file list area that becomes visible when files are selected
- A submit button
- A bottom navigation bar
- The JavaScript that implements drag/drop, renders selected files, and handles submit click

It also includes these CSS links in the `<head>`:
- `'/static/css/tutor_verifiaction.css'`
  - Contains extracted CSS rules from the original HTML’s `<style>` blocks.
- `'/static/css/tutor_verification_student.css'`
  - Added to make the page look more similar to a student-style UI in this project.

#### Key HTML elements
- **Drag/Drop upload zone**
  - `id="drop-zone"`
  - Clicking it triggers:
    ```html
    onclick="document.getElementById('file-input').click()"
    ```
  - The hidden file input is:
    ```html
    <input id="file-input" type="file" accept=".pdf,.jpg,.jpeg,.png" multiple class="hidden" />
    ```

- **File list container**
  - `id="file-list"`
  - Starts hidden:
    ```html
    <div id="file-list" class="hidden"></div>
    ```

- **Submit button**
  - `id="submit-btn"`
  - On click, it changes button text and disables the button, then shows an alert and reloads the page.

---

### 2) `static/css/tutor_verifiaction.css`
This stylesheet contains extracted CSS rules from the original HTML.

It includes:
- `.material-symbols-outlined`:
  - Sets the font variation settings so the Material Symbols icons render consistently.
- `.drag-active`:
  - Styling used during drag-and-drop.
- `body` min-height rule:
  - Ensures the page fills tall screens properly.

---

### 3) `static/css/tutor_verification_student.css`
This stylesheet is **new** and is used to give the page a more “student-like” look.

It applies simple styles such as:
- Page background + text color
- “Card” style look (rounded corners, subtle border/shadow)
- Upload zone dashed border
- Primary button styling
- File row styling

> Note: The page still uses Tailwind utility classes from the CDN. This extra CSS file only provides additional base styling so the overall look matches the student UI style more closely.

---

## 4) `app.py`
A new Flask route was added so the page is accessible.

Route added:
- `GET /tutor_verification`
  - Returns `render_template('tutor_Verification.html')`

This allows you to open the verification page at:
- `http://127.0.0.1:5000/tutor_verification`

---

## JavaScript blocks in `tutor_Verification.html`
The JS implements three main behaviors.

### A) Drag & Drop event binding
It registers handlers for:
- `dragenter`
- `dragover`
- `dragleave`
- `drop`

The helper `preventDefaults(e)` cancels default browser behavior so dropping works correctly.

### B) Drag UI feedback
On `dragenter` / `dragover`, it adds:
- `dropZone.classList.add('drag-active')`

On `dragleave` / `drop`, it removes:
- `dropZone.classList.remove('drag-active')`

The visual effect is controlled by the `.drag-active` rule in `tutor_verifiaction.css`.

### C) File selection + file list rendering
When files are selected (or dropped), `handleFiles(e)`:
1. Converts the file list to an array:
   ```js
   const files = [...e.target.files];
   ```
2. If there are files, it shows the file list container:
   ```js
   fileList.classList.remove('hidden');
   ```
3. For each file, it creates a row `<div>` and injects HTML with the file name and size.
4. Each file row includes a delete button that removes the row from the DOM.

### D) Submit button behavior
On submit click:
- Button text changes to `Uploading...`
- Button is disabled
- After 1.5 seconds:
  - Shows an alert
  - Reloads the page

---

## Result / Expected behavior
- User can click the upload zone or drag files into it.
- Files appear in a list with size information.
- Files can be removed before submit.
- Clicking submit triggers the alert + reload.
- Page loads with external CSS from:
  - `static/css/tutor_verifiaction.css`
  - `static/css/tutor_verification_student.css`

---

## Notes
- The submit action is currently simulated (client-side only) using `setTimeout` and `alert()`; there is no server-side upload implemented in this task.
- The route only renders the page template; no files are uploaded to the backend yet.

