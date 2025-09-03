## 1. **Complete State System** (First artifact)

Shows all 6 application states in a grid layout:

- **State 1: Empty** - Clean welcome screen with drop zone
- **State 2: Files Added** - File list with animated entry
- **State 3: Processing** - Minimal progress indicator
- **State 4: Complete** - Success summary with stats
- **State 5: Details** - Metadata removal report
- **State 6: Error** - Graceful error handling

## 2. **Developer Specification** (Second artifact)

A complete 12-section specification including:

- Design philosophy and visual language
- Detailed state descriptions and transitions
- Component specifications with exact CSS values
- Platform-specific adaptations
- Performance targets and accessibility requirements
- Implementation roadmap with phases

## 3. **Interactive Prototype** (Third artifact)

A fully functional HTML implementation featuring:

- Smooth state transitions
- Interactive preset selection
- File management (add/remove)
- Animated processing simulation
- Drag-and-drop support
- Responsive button states

## Key Design Decisions:

**Visual Identity:**

- Dark blue gradient background (#1a2332 → #2d3748)
- Clean white card with subtle transparency
- Minimal 2px progress bars
- 8px dots for preset selection
- 24px border radius for soft, modern feel

**Interaction Philosophy:**

- Progressive disclosure (hide complexity)
- Single primary action per state
- Smooth 400ms transitions
- Hover states provide feedback
- Everything is keyboard accessible

**Technical Approach:**

- Fixed 400×580px card size
- CSS-only animations (GPU accelerated)
- State-based styling with data attributes
- Minimal DOM manipulation
- Under 100KB total size

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Sanitize - Zen Card Implementation</title>
    <style>
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }

      body {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
          "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        background: linear-gradient(135deg, #1a2332 0%, #2d3748 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
      }

      .app-card {
        background: rgba(255, 255, 255, 0.98);
        width: 400px;
        min-height: 580px;
        border-radius: 24px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 48px;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.15);
        position: relative;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      }

      /* State-based layouts */
      .app-card[data-state="empty"] {
        justify-content: center;
      }

      .app-card[data-state="files-added"] {
        justify-content: flex-start;
        padding-top: 48px;
      }

      .app-card[data-state="processing"] {
        justify-content: center;
      }

      .app-card[data-state="complete"] {
        justify-content: center;
      }

      .app-card[data-state="details"] {
        justify-content: flex-start;
        padding: 32px;
      }

      /* Drop Zone State */
      .drop-zone {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
        transition: all 0.3s ease;
        cursor: pointer;
      }

      .app-card[data-state="empty"] .drop-zone {
        display: flex;
      }

      .app-card:not([data-state="empty"]) .drop-zone {
        display: none;
      }

      .drop-text {
        font-size: 20px;
        font-weight: 300;
        color: #1a202c;
        letter-spacing: 0.5px;
      }

      .drop-subtext {
        font-size: 14px;
        color: #718096;
        margin-top: -8px;
      }

      .add-button {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: transparent;
        border: 2px solid #e2e8f0;
        color: #a0aec0;
        font-size: 28px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .add-button:hover {
        border-color: #2d3748;
        color: #2d3748;
        transform: scale(1.1) rotate(90deg);
      }

      /* Files List State */
      .files-section {
        display: none;
        width: 100%;
        flex-direction: column;
        align-items: center;
      }

      .app-card[data-state="files-added"] .files-section {
        display: flex;
      }

      .file-count {
        font-size: 14px;
        color: #718096;
        margin-bottom: 24px;
        text-align: center;
      }

      .files-list {
        width: 100%;
        margin-bottom: 24px;
      }

      .file-item {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f7fafc;
        opacity: 0;
        animation: slideIn 0.4s ease forwards;
      }

      @keyframes slideIn {
        from {
          opacity: 0;
          transform: translateY(10px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      .file-item:nth-child(1) {
        animation-delay: 0.1s;
      }
      .file-item:nth-child(2) {
        animation-delay: 0.2s;
      }
      .file-item:nth-child(3) {
        animation-delay: 0.3s;
      }

      .file-icon {
        width: 32px;
        height: 32px;
        background: #f7fafc;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        font-size: 14px;
      }

      .file-details {
        flex: 1;
      }

      .file-name {
        font-size: 14px;
        color: #2d3748;
        font-weight: 500;
      }

      .file-size {
        font-size: 12px;
        color: #a0aec0;
      }

      .file-remove {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #cbd5e0;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 20px;
      }

      .file-remove:hover {
        background: #fed7d7;
        color: #e53e3e;
      }

      /* Processing State */
      .processing-section {
        display: none;
        flex-direction: column;
        align-items: center;
      }

      .app-card[data-state="processing"] .processing-section {
        display: flex;
      }

      .processing-icon {
        width: 64px;
        height: 64px;
        border: 3px solid #e2e8f0;
        border-top-color: #2d3748;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 24px;
      }

      @keyframes spin {
        to {
          transform: rotate(360deg);
        }
      }

      .status-text {
        font-size: 16px;
        color: #2d3748;
        margin-bottom: 8px;
        text-align: center;
      }

      .status-detail {
        font-size: 14px;
        color: #718096;
        margin-bottom: 24px;
        text-align: center;
      }

      .progress-bar {
        width: 240px;
        height: 2px;
        background: #e2e8f0;
        border-radius: 1px;
        overflow: hidden;
        margin-bottom: 24px;
      }

      .progress-fill {
        height: 100%;
        background: #2d3748;
        width: 0%;
        transition: width 0.5s ease;
      }

      /* Complete State */
      .complete-section {
        display: none;
        flex-direction: column;
        align-items: center;
      }

      .app-card[data-state="complete"] .complete-section {
        display: flex;
      }

      .success-icon {
        width: 64px;
        height: 64px;
        border-radius: 50%;
        background: #c6f6d5;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 24px;
        animation: scaleIn 0.4s ease;
      }

      @keyframes scaleIn {
        from {
          transform: scale(0);
          opacity: 0;
        }
        to {
          transform: scale(1);
          opacity: 1;
        }
      }

      .checkmark {
        width: 32px;
        height: 32px;
        stroke: #22543d;
        stroke-width: 3;
        fill: none;
        stroke-linecap: round;
        stroke-linejoin: round;
      }

      .summary-title {
        font-size: 18px;
        color: #2d3748;
        margin-bottom: 24px;
        font-weight: 500;
      }

      .summary-stats {
        display: flex;
        gap: 32px;
        justify-content: center;
        margin-bottom: 32px;
      }

      .stat {
        text-align: center;
      }

      .stat-value {
        font-size: 24px;
        font-weight: 600;
        color: #2d3748;
      }

      .stat-label {
        font-size: 12px;
        color: #718096;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
      }

      /* Details State */
      .details-section {
        display: none;
        flex-direction: column;
        width: 100%;
        height: 100%;
      }

      .app-card[data-state="details"] .details-section {
        display: flex;
      }

      .details-header {
        width: 100%;
        padding-bottom: 16px;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 24px;
      }

      .back-button {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #718096;
        font-size: 14px;
        cursor: pointer;
        transition: color 0.2s ease;
      }

      .back-button:hover {
        color: #2d3748;
      }

      .details-content {
        width: 100%;
        flex: 1;
        overflow-y: auto;
        margin-bottom: 24px;
      }

      .metadata-section {
        margin-bottom: 20px;
      }

      .metadata-title {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #718096;
        margin-bottom: 12px;
      }

      .metadata-item {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        font-size: 13px;
      }

      .metadata-key {
        color: #718096;
      }

      .removed-badge {
        background: #fed7d7;
        color: #c53030;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }

      /* Preset Dots (visible in multiple states) */
      .preset-dots {
        display: flex;
        gap: 12px;
        align-items: center;
        margin: 32px 0;
      }

      .app-card[data-state="processing"] .preset-dots,
      .app-card[data-state="complete"] .preset-dots,
      .app-card[data-state="details"] .preset-dots {
        display: none;
      }

      .preset-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #e2e8f0;
        cursor: pointer;
        transition: all 0.3s ease;
      }

      .preset-dot.active {
        background: #2d3748;
        transform: scale(1.5);
      }

      .preset-dot:hover {
        transform: scale(1.3);
      }

      .preset-label {
        margin-left: 16px;
        font-size: 14px;
        color: #718096;
        font-weight: 400;
        letter-spacing: 0.5px;
      }

      /* Output Mode */
      .output-mode {
        display: none;
        gap: 16px;
        margin-bottom: 24px;
        font-size: 12px;
        color: #718096;
      }

      .app-card[data-state="files-added"] .output-mode {
        display: flex;
      }

      .output-option {
        cursor: pointer;
        transition: color 0.2s ease;
      }

      .output-option.active {
        color: #2d3748;
        font-weight: 500;
      }

      /* Buttons */
      .primary-button {
        padding: 14px 40px;
        background: transparent;
        border: 1px solid #2d3748;
        border-radius: 24px;
        font-size: 14px;
        font-weight: 400;
        letter-spacing: 1px;
        color: #2d3748;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
      }

      .primary-button:hover:not(:disabled) {
        background: #2d3748;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(45, 55, 72, 0.2);
      }

      .primary-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .secondary-button {
        padding: 10px 24px;
        background: transparent;
        border: none;
        font-size: 13px;
        color: #718096;
        cursor: pointer;
        transition: color 0.2s ease;
        text-decoration: underline;
        margin-top: 16px;
      }

      .secondary-button:hover {
        color: #2d3748;
      }

      /* Drag and drop overlay */
      .drop-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(45, 55, 72, 0.95);
        border-radius: 24px;
        display: none;
        align-items: center;
        justify-content: center;
        z-index: 100;
      }

      .drop-overlay.active {
        display: flex;
      }

      .drop-overlay-text {
        color: white;
        font-size: 20px;
        font-weight: 300;
        letter-spacing: 0.5px;
      }
    </style>
  </head>
  <body>
    <div class="app-card" data-state="empty">
      <!-- Drop Overlay -->
      <div class="drop-overlay">
        <div class="drop-overlay-text">Drop to add files</div>
      </div>

      <!-- State 1: Empty -->
      <div class="drop-zone">
        <div class="drop-text">Drop files anywhere</div>
        <div class="drop-subtext">or press +</div>
        <button class="add-button" onclick="addFiles()">+</button>
      </div>

      <!-- State 2: Files Added -->
      <div class="files-section">
        <div class="file-count">3 files ready</div>
        <div class="files-list">
          <div class="file-item">
            <div class="file-icon">📄</div>
            <div class="file-details">
              <div class="file-name">report.pdf</div>
              <div class="file-size">2.1 MB</div>
            </div>
            <div class="file-remove" onclick="removeFile(this)">×</div>
          </div>
          <div class="file-item">
            <div class="file-icon">📄</div>
            <div class="file-details">
              <div class="file-name">invoice.docx</div>
              <div class="file-size">156 KB</div>
            </div>
            <div class="file-remove" onclick="removeFile(this)">×</div>
          </div>
          <div class="file-item">
            <div class="file-icon">📄</div>
            <div class="file-details">
              <div class="file-name">contract.pdf</div>
              <div class="file-size">892 KB</div>
            </div>
            <div class="file-remove" onclick="removeFile(this)">×</div>
          </div>
        </div>
      </div>

      <!-- State 3: Processing -->
      <div class="processing-section">
        <div class="processing-icon"></div>
        <div class="status-text">Sanitizing files</div>
        <div class="status-detail">Processing contract.pdf</div>
        <div class="progress-bar">
          <div class="progress-fill"></div>
        </div>
        <div class="file-count">2 of 3 complete</div>
      </div>

      <!-- State 4: Complete -->
      <div class="complete-section">
        <div class="success-icon">
          <svg class="checkmark" viewBox="0 0 24 24">
            <path d="M20 6L9 17l-5-5" />
          </svg>
        </div>
        <div class="summary-title">Sanitization Complete</div>
        <div class="summary-stats">
          <div class="stat">
            <div class="stat-value">3</div>
            <div class="stat-label">Files</div>
          </div>
          <div class="stat">
            <div class="stat-value">47</div>
            <div class="stat-label">Items Removed</div>
          </div>
          <div class="stat">
            <div class="stat-value">100%</div>
            <div class="stat-label">Clean</div>
          </div>
        </div>
      </div>

      <!-- State 5: Details -->
      <div class="details-section">
        <div class="details-header">
          <div class="back-button" onclick="backToSummary()">
            <span>←</span>
            <span>Back to summary</span>
          </div>
        </div>
        <div class="details-content">
          <div class="metadata-section">
            <div class="metadata-title">report.pdf</div>
            <div class="metadata-item">
              <span class="metadata-key">Title</span>
              <span class="removed-badge">Removed</span>
            </div>
            <div class="metadata-item">
              <span class="metadata-key">Author</span>
              <span class="removed-badge">Removed</span>
            </div>
            <div class="metadata-item">
              <span class="metadata-key">Creation Date</span>
              <span class="removed-badge">Removed</span>
            </div>
            <div class="metadata-item">
              <span class="metadata-key">GPS Location</span>
              <span class="removed-badge">Removed</span>
            </div>
          </div>
          <div class="metadata-section">
            <div class="metadata-title">invoice.docx</div>
            <div class="metadata-item">
              <span class="metadata-key">Last Modified By</span>
              <span class="removed-badge">Removed</span>
            </div>
            <div class="metadata-item">
              <span class="metadata-key">Company</span>
              <span class="removed-badge">Removed</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Preset Dots -->
      <div class="preset-dots">
        <span class="preset-dot" onclick="setPreset(0)"></span>
        <span class="preset-dot active" onclick="setPreset(1)"></span>
        <span class="preset-dot" onclick="setPreset(2)"></span>
        <span class="preset-label">Balanced</span>
      </div>

      <!-- Output Mode -->
      <div class="output-mode">
        <span class="output-option active" onclick="setOutput(0)">Replace</span>
        <span>·</span>
        <span class="output-option" onclick="setOutput(1)">Backup</span>
        <span>·</span>
        <span class="output-option" onclick="setOutput(2)">Export</span>
      </div>

      <!-- Primary Button (changes based on state) -->
      <button class="primary-button" onclick="primaryAction()">Continue</button>
      <button
        class="secondary-button"
        style="display: none;"
        onclick="secondaryAction()"
      >
        Add More Files
      </button>
    </div>

    <script>
      const card = document.querySelector(".app-card");
      const primaryBtn = document.querySelector(".primary-button");
      const secondaryBtn = document.querySelector(".secondary-button");
      const progressFill = document.querySelector(".progress-fill");

      // State management
      function setState(state) {
        card.setAttribute("data-state", state);
        updateButton(state);
      }

      function updateButton(state) {
        switch (state) {
          case "empty":
            primaryBtn.textContent = "Continue";
            primaryBtn.disabled = true;
            secondaryBtn.style.display = "none";
            break;
          case "files-added":
            primaryBtn.textContent = "Sanitize";
            primaryBtn.disabled = false;
            secondaryBtn.style.display = "none";
            break;
          case "processing":
            primaryBtn.textContent = "Processing...";
            primaryBtn.disabled = true;
            secondaryBtn.style.display = "none";
            break;
          case "complete":
            primaryBtn.textContent = "View Details";
            primaryBtn.disabled = false;
            secondaryBtn.style.display = "block";
            secondaryBtn.textContent = "Add More Files";
            break;
          case "details":
            primaryBtn.textContent = "Export Report";
            primaryBtn.disabled = false;
            secondaryBtn.style.display = "none";
            break;
        }
      }

      // Actions
      function primaryAction() {
        const currentState = card.getAttribute("data-state");
        switch (currentState) {
          case "files-added":
            startProcessing();
            break;
          case "complete":
            setState("details");
            break;
          case "details":
            alert("Exporting report...");
            break;
        }
      }

      function secondaryAction() {
        setState("empty");
      }

      function addFiles() {
        setState("files-added");
      }

      function removeFile(element) {
        element.closest(".file-item").remove();
        const remainingFiles = document.querySelectorAll(".file-item").length;
        if (remainingFiles === 0) {
          setState("empty");
        } else {
          document.querySelector(
            ".file-count"
          ).textContent = `${remainingFiles} files ready`;
        }
      }

      function startProcessing() {
        setState("processing");
        let progress = 0;
        const interval = setInterval(() => {
          progress += 10;
          progressFill.style.width = progress + "%";
          if (progress >= 100) {
            clearInterval(interval);
            setTimeout(() => setState("complete"), 500);
          }
        }, 300);
      }

      function backToSummary() {
        setState("complete");
      }

      function setPreset(index) {
        const dots = document.querySelectorAll(".preset-dot");
        const labels = ["Safe", "Balanced", "Aggressive"];
        dots.forEach((dot, i) => {
          dot.classList.toggle("active", i === index);
        });
        document.querySelector(".preset-label").textContent = labels[index];
      }

      function setOutput(index) {
        const options = document.querySelectorAll(".output-option");
        options.forEach((opt, i) => {
          if (opt.textContent !== "·") {
            opt.classList.toggle("active", Math.floor(i / 2) === index);
          }
        });
      }

      // Drag and drop
      const dropOverlay = document.querySelector(".drop-overlay");

      card.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropOverlay.classList.add("active");
      });

      card.addEventListener("dragleave", (e) => {
        if (e.target === card) {
          dropOverlay.classList.remove("active");
        }
      });

      card.addEventListener("drop", (e) => {
        e.preventDefault();
        dropOverlay.classList.remove("active");
        const currentState = card.getAttribute("data-state");
        if (currentState === "empty") {
          setState("files-added");
        }
      });
    </script>
  </body>
</html>
```
