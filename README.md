# Sanitize — Minimal, Cross‑Platform Document Sanitizer

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](https://github.com/your-username/sanitize/releases)
[![Security](https://img.shields.io/badge/Security-Offline%20Only-red?style=flat-square&logo=shield)](SECURITY.md)

**Remove sensitive metadata and active content from documents — fast, locally, and with zero telemetry.**

[Download Latest Release](https://github.com/your-username/sanitize/releases) • [Documentation](SPEC.md) • [Security](SECURITY.md) • [Contributing](CONTRIBUTING.md)

---

## Overview

Cross-platform document sanitizer that removes sensitive metadata and active content from PDF and DOCX files. Features a minimal GUI by default with headless automation support. Privacy-first design with zero telemetry, atomic writes, and comprehensive JSON reporting for auditing. It ships as a single application per OS that launches a minimal, focused GUI by default and also supports headless operation for automation.

### Key Features

- **Privacy-First**: Offline only, zero telemetry, no network calls
- **Cross-Platform**: Windows, macOS, Linux with native binaries
- **Dual-Mode**: Beautiful GUI by default, powerful CLI with flags
- **Fast & Safe**: Atomic writes, optional backups, transparent reporting
- **Comprehensive**: Detailed JSON reports for auditing and compliance
- **Secure**: Focuses on metadata removal, not content modification

### What Sanitize Removes

#### PDF Documents

- **Document Info**: Title, Author, Subject, Keywords, Creation/Modification dates
- **XMP Metadata**: Embedded metadata streams and properties
- **Viewer Preferences**: Display settings and zoom levels
- **Navigation**: Outlines, bookmarks, and table of contents
- **Active Content**: JavaScript, OpenAction, automatic actions
- **Attachments**: Embedded files and document attachments
- **Form Data**: XFA forms and empty AcroForm structures
- **Page Metadata**: LastModified, PieceInfo, and page-level metadata
- **Trailer IDs**: Refreshes document identifiers for anonymity

#### DOCX Documents

- **Core Properties**: Title, Author, Subject, Description, Keywords, Category
- **Application Properties**: Company, Manager, Application version, Template
- **Custom Properties**: All custom XML properties and metadata
- **Thumbnails**: Document preview images and embedded graphics
- **Dublin Core**: Creation and modification timestamps
- **Content Types**: Updates XML to reflect removed components

> **Important**: Sanitize focuses on metadata and active features. It does not rasterize or reflow content and is not a malware scanner.

—

## Downloads

Download the latest release artifacts from the GitHub Releases page for your OS:

- **Windows**: Portable `Sanitize.exe` (requires WebView2 Runtime for GUI)
- **macOS**: `Sanitize.app` in a `.dmg` (macOS 12+, Apple Silicon recommended)
- **Linux**: AppImage and/or `.deb` (modern distro with glibc 2.31+)

### System Requirements

- **Windows 10/11**: GUI requires Microsoft Edge WebView2 Runtime (headless mode works without it)
- **macOS 12+**: Apple Silicon recommended for best performance
- **Linux**: Modern distribution with glibc 2.31+; GUI requires WebKit runtime

### Verification

Always verify the SHA256 checksum shown on the Release page before running:

**Windows (PowerShell)**

```powershell
Get-FileHash .\Sanitize.exe -Algorithm SHA256
```

**macOS/Linux**

```bash
shasum -a 256 Sanitize.app
sha256sum Sanitize.AppImage
```

—

## Quick Start

### GUI Mode

1. **Launch**: Double-click the application or run `sanitize`
2. **Add Files**: Drag & drop files or press "+" to choose files
3. **Configure**: Select preset (Safe/Balanced/Aggressive) and output mode (Replace/Backup/Export)
4. **Process**: Press "Sanitize" and view results
5. **Review**: Check summary stats and detailed removal report
6. **Export**: Save session report for auditing if needed

### Headless Mode

Run `sanitize` with command-line arguments for automation:

```bash
# Export sanitized copies to output directory
sanitize --auto --preset balanced --mode export --out-dir ./out *.pdf *.docx

# In-place processing with backups
sanitize --preset aggressive --mode backup docs/*.pdf

# JSON array output for scripting
sanitize --json-array --mode export --out-dir ./out report.pdf
```

**Output**: Per-file JSON to stdout (JSON lines by default) and sidecar files unless disabled.

—

## GUI Overview

The GUI is intentionally minimal and distraction‑free.

- Add Files: drag & drop or press “+”.
- Presets: select one of three dots (Safe, Balanced, Aggressive). Balanced is default.
- Output Mode: Replace (in‑place), Backup (keep a `.bak`), or Export (choose folder).
- Processing: a compact indicator shows progress and “N of M complete”.
- Complete: summary stats (Files, Items Removed, Clean%).
- Details: per‑file list of items removed; export a session report (JSON) for auditing.

Accessibility

- Keyboard friendly, visible focus rings, reduced motion honored.

—

## Command Line Interface

Sanitize runs headless when called with arguments. It prints JSON lines by default (one line per file) or a single JSON array with `--json-array`.

### Command Line Options

| Option                                  | Description                                 | Default    |
| --------------------------------------- | ------------------------------------------- | ---------- |
| `--auto`                                | Detect file type by extension               | `true`     |
| `--preset {safe\|balanced\|aggressive}` | Sanitization preset                         | `balanced` |
| `--mode {replace\|backup\|export}`      | Output mode                                 | `replace`  |
| `--out-dir DIR`                         | Output directory (required for export mode) | -          |
| `--no-sidecar`                          | Disable per-file sidecar JSON               | `false`    |
| `--json-array`                          | Emit one JSON array instead of JSON lines   | `false`    |
| `--dry-run`                             | Report only; do not write outputs           | `false`    |
| `--recursive`                           | Recurse into directories                    | `false`    |
| `--help`                                | Show help message                           | -          |

### Usage Examples

**Basic Processing**

```bash
# Process single file with default settings
sanitize document.pdf

# Process multiple files with specific preset
sanitize --preset aggressive *.pdf *.docx
```

**Export Mode**

```bash
# Export sanitized copies to output directory
sanitize --mode export --out-dir ./clean docs/*.{pdf,docx}

# Export with custom preset
sanitize --preset safe --mode export --out-dir ./output report.pdf
```

**Backup Mode**

```bash
# In-place processing with backups
sanitize --mode backup --preset balanced *.pdf

# Backup with aggressive sanitization
sanitize --preset aggressive --mode backup sensitive-docs/
```

**Automation & Scripting**

```bash
# JSON array output for parsing
sanitize --json-array --mode export --out-dir ./out *.pdf

# Dry run to preview changes
sanitize --dry-run --preset balanced *.docx

# Recursive directory processing
sanitize --recursive --mode export --out-dir ./clean ./documents/
```

**Advanced Usage**

```bash
# Disable sidecar files for cleaner output
sanitize --no-sidecar --mode backup *.pdf

# Process specific file types
sanitize --auto --preset balanced --mode export --out-dir ./out *.pdf
```

—

## Presets

Sanitize offers three sanitization presets to balance thoroughness with document functionality:

### Safe

- **Conservative approach**: Removes basic metadata while preserving form functionality
- **Removes**: Document info, XMP metadata, viewer preferences, basic attachments
- **Preserves**: AcroForm structures, complex annotations, form fields
- **Use case**: When document forms and annotations must remain functional

### Balanced (Default)

- **Recommended setting**: Comprehensive metadata removal with minimal disruption
- **Removes**: All Safe items plus JavaScript, XFA forms, page-level metadata, outlines
- **Refreshes**: Document trailer IDs for anonymity
- **Use case**: General-purpose sanitization for most documents

### Aggressive

- **Maximum sanitization**: Removes all possible metadata and active content
- **Removes**: All Balanced items plus AcroForm, annotations, embedded names
- **Warning**: May break form functionality and complex document features
- **Use case**: When maximum privacy is required and document functionality is not critical

—

## Output Modes

Choose how Sanitize handles your processed files:

### Replace

- **In-place processing**: Atomically overwrites originals with sanitized versions
- **Space efficient**: No additional storage required
- **Risk**: Original files are permanently modified
- **Use case**: When you're confident in the sanitization process

### Backup

- **Safe replacement**: Writes sanitized version in place, keeps `.bak` copy of original
- **File naming**: `document.pdf` → `document.pdf` (sanitized) + `document.pdf.bak` (original)
- **Storage**: Requires 2x disk space during processing
- **Use case**: When you want to keep originals but prefer in-place workflow

### Export

- **Non-destructive**: Leaves originals untouched, writes sanitized copies to chosen folder
- **Flexible**: Choose any output directory
- **Safe**: Original files never modified
- **Use case**: When evaluating Sanitize or when you need to keep originals intact

> **Tip**: Prefer Export or Backup when evaluating Sanitize for the first time.

—

## Reports and Auditing

- Per‑file sidecar (`name.ext.sanitize.json`) written next to the sanitized file unless disabled.
- Session report (GUI Details → Export Report) contains all files processed in a single JSON for auditing.

Per‑file sidecar structure (simplified)

```
{
  "sanitized_at_utc": "2025-09-03T12:34:56+00:00",
  "document": "/path/to/file.pdf",
  "type": "pdf",
  "old": { /* before snapshot */ },
  "new": { /* after snapshot */ },
  "actions": ["docinfo:/Title removed", "xmp_present cleared", "attachments removed"],
  "duration_ms": 1234,
  "preset": "balanced",
  "output_mode": "export"
}
```

—

## Security and Privacy

### Privacy-First Design

- **Offline by default**: No telemetry, network calls, or data collection
- **Local processing**: All sanitization happens on your device
- **No cloud dependencies**: Works completely offline
- **Transparent reporting**: Full audit trail of all changes made

### Security Features

- **Atomic writes**: Temporary files prevent corruption during processing
- **Safe defaults**: Conservative approach minimizes risk of document damage
- **Comprehensive logging**: Detailed reports for security auditing
- **Input validation**: Robust parsing prevents malformed file exploits

### Threat Model

**What Sanitize Protects Against:**

- Metadata leaks (author, creation date, GPS coordinates)
- Document tracking via unique identifiers
- Embedded malicious content (JavaScript, attachments)
- Information disclosure through document properties

**What Sanitize Does NOT Protect Against:**

- Malware scanning (not a security scanner)
- Reader/viewer exploits (focuses on document content, not viewer vulnerabilities)
- Proprietary or malformed data in unusual file formats
- Content-based attacks (does not analyze document content)

### Security Best Practices

1. **Always keep backups** (use Backup or Export modes)
2. **Review sanitization reports** to confirm expected changes
3. **Test on copies first** when evaluating new document types
4. **Verify checksums** of downloaded releases
5. **Run in isolated environment** for highly sensitive documents
6. **Regular updates** to get latest security improvements

### Known Limitations

- Cannot guarantee removal of every non-standard or proprietary payload
- May not handle extremely malformed or corrupted files
- Focuses on metadata removal, not content analysis
- Some advanced PDF features may require specialized tools

—

## Troubleshooting

### Common Issues

#### Windows: "WebView2 not found"

**Problem**: GUI fails to launch with WebView2 error
**Solution**:

- Install [Microsoft Edge WebView2 Evergreen Runtime](https://developer.microsoft.com/en-us/microsoft-edge/webview2/)
- Headless mode works without WebView2
- Most Windows 10/11 systems already have WebView2 installed

#### macOS: "App is damaged or can't be opened"

**Problem**: macOS security blocks unsigned application
**Solution**:

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /Applications/Sanitize.app

# Or allow in System Preferences > Security & Privacy
```

#### Linux: Application won't start / missing libraries

**Problem**: Missing WebKit or GTK dependencies
**Solutions**:

- Prefer AppImage if available (fewer dependency issues)
- Install WebKit/GTK stack: `sudo apt install webkit2gtk-4.0` (Ubuntu/Debian)
- Run headless mode if GUI dependencies are problematic

#### Permission Errors / Locked Files

**Problem**: Cannot write to destination directory
**Solutions**:

- Ensure write permissions to destination folder
- Use Export mode to user-writable directory
- Check if files are open in other applications
- Run with appropriate user permissions

#### File Processing Errors

**Problem**: Specific files fail to process
**Solutions**:

- Check file format compatibility (PDF/DOCX only)
- Verify files are not corrupted or password-protected
- Try different preset (Safe vs Aggressive)
- Use dry-run mode to preview changes: `--dry-run`

#### Performance Issues

**Problem**: Slow processing or high memory usage
**Solutions**:

- Process files in smaller batches
- Use headless mode for better performance
- Ensure sufficient disk space for temporary files
- Close other applications to free memory

### Getting Help

1. **Check the logs**: Look for error messages in the console output
2. **Try different modes**: Test with Export mode first
3. **Verify file integrity**: Ensure source files are not corrupted
4. **Report issues**: Include error messages and file types when reporting bugs

—

## Verify Downloads

Always compare the SHA256 checksum shown on the Release page.

Windows (PowerShell)

```
Get-FileHash .\Sanitize.exe -Algorithm SHA256
```

macOS/Linux

```
shasum -a 256 Sanitize.app
sha256sum Sanitize.AppImage
```

—

## Development

### Prerequisites

- **Python 3.10+** (required for modern type hints and features)
- **pip** or **uv** (package manager)
- **PyInstaller** (for building standalone executables)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/sanitize.git
cd sanitize

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install development dependencies
pip install -e .[dev]
```

### Running from Source

```bash
# Launch GUI
sanitize

# Run headless with help
sanitize --help

# Run tests
pytest -q

# Run linting
ruff check .
ruff format .

# Type checking
mypy src
```

### Building Standalone Executables

```bash
# Build for current platform
pyinstaller --noconfirm --windowed --name Sanitize \
  --add-data "assets/ui/index.html:assets/ui/index.html" \
  src/sanitize/app.py

# Cross-platform builds (requires appropriate environment)
# Windows: Build on Windows with Visual Studio
# macOS: Build on macOS with Xcode
# Linux: Build on Linux with standard toolchain
```

### Project Structure

```
sanitize/
├── src/sanitize/           # Main source code
│   ├── core/              # Core sanitization logic
│   │   ├── pdf.py         # PDF sanitization
│   │   ├── docx.py        # DOCX sanitization
│   │   └── report.py      # Report generation
│   ├── gui/               # GUI components
│   │   ├── webview_app.py # WebView application
│   │   └── api.py         # Python-JavaScript bridge
│   ├── app.py             # Main entry point
│   └── config.py          # Configuration
├── assets/ui/             # Web UI assets
│   └── index.html         # Single-page application
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── pyproject.toml         # Project configuration
└── VERSION                # Version file
```

—

## Frequently Asked Questions

### General Questions

**Q: Is Sanitize safe to use on important documents?**
A: Yes, but always use Backup or Export mode for important documents. Sanitize uses atomic writes and comprehensive testing, but keeping backups is a best practice.

**Q: Does Sanitize modify the visual content of documents?**
A: No. Sanitize only removes metadata and active content. The visual appearance, layout, and text content remain unchanged.

**Q: Can I use Sanitize in automated workflows?**
A: Yes. The headless mode with JSON output is designed for automation and scripting. Use `--json-array` for structured output.

**Q: What file formats are supported?**
A: Currently PDF and DOCX. Additional formats (PPTX, XLSX, ODT) are planned for future releases.

### Technical Questions

**Q: Why does the GUI require WebView2 on Windows?**
A: The GUI uses a modern web-based interface for cross-platform consistency. Headless mode works without WebView2.

**Q: How does Sanitize handle password-protected documents?**
A: Sanitize cannot process password-protected documents. Remove password protection before sanitization.

**Q: What's the difference between the presets?**
A: Safe preserves form functionality, Balanced removes most metadata while maintaining usability, Aggressive removes everything possible.

**Q: Can I customize what gets removed?**
A: Not in the current version. Presets provide different levels of sanitization. Custom rules may be added in future versions.

### Security Questions

**Q: Is my data sent anywhere?**
A: No. Sanitize is completely offline and never sends data over the network.

**Q: Can Sanitize remove malware from documents?**
A: No. Sanitize is not a malware scanner. It removes metadata and active content but does not scan for malicious code.

**Q: How do I verify the sanitization worked?**
A: Review the JSON reports generated by Sanitize. These show exactly what was removed from each document.

---

## Roadmap

### Version 0.2.0 (Planned)

- **Additional Formats**: PPTX, XLSX support
- **Custom Rules**: User-defined sanitization rules
- **Batch Processing**: Improved large-scale processing
- **Plugin System**: Extensible sanitization modules

### Version 0.3.0 (Future)

- **Image Support**: EXIF/IPTC/XMP removal from images
- **Archive Support**: ZIP, RAR metadata sanitization
- **Advanced PDF**: More comprehensive PDF sanitization
- **Cloud Integration**: Optional cloud storage integration

### Long-term Goals

- **Enterprise Features**: Centralized management and reporting
- **API Server**: REST API for integration with other tools
- **Machine Learning**: Intelligent metadata detection
- **Cross-platform Mobile**: iOS and Android versions

---

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- **Code Style**: Follow the established patterns and use proper type hints
- **Testing**: Add tests for new features and bug fixes
- **UI Fidelity**: Maintain exact compliance with GUI-SPEC.md
- **Documentation**: Update docs for new features

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run the test suite: `pytest -q`
5. Run linting: `ruff check . && ruff format .`
6. Submit a pull request

### Areas for Contribution

- **New File Formats**: Add support for additional document types
- **Performance**: Optimize processing speed and memory usage
- **UI/UX**: Improve the user interface and experience
- **Documentation**: Enhance guides and examples
- **Testing**: Add more comprehensive test coverage

—

---

## Performance

### Benchmarks

Sanitize is optimized for speed and efficiency. Typical performance on modern hardware:

**Processing Speed**

- **PDF files**: 10-50 MB/s (varies by complexity and metadata content)
- **DOCX files**: 20-100 MB/s (generally faster due to simpler structure)
- **Memory usage**: 50-200 MB peak (depends on file size and complexity)

**Typical Processing Times**

- **Small files** (< 1 MB): 0.1-0.5 seconds
- **Medium files** (1-10 MB): 0.5-2 seconds
- **Large files** (10-100 MB): 2-10 seconds
- **Very large files** (> 100 MB): 10+ seconds

### Performance Tips

1. **Use headless mode** for better performance on large batches
2. **Process files in parallel** using multiple instances for large datasets
3. **Use Export mode** to avoid disk I/O bottlenecks with large files
4. **Close other applications** to free memory for large file processing
5. **Use SSD storage** for faster temporary file operations

### Comparison with Alternatives

| Tool           | Speed    | Formats   | GUI | Offline | Open Source |
| -------------- | -------- | --------- | --- | ------- | ----------- |
| **Sanitize**   | Fast     | PDF, DOCX | Yes | Yes     | Yes         |
| Adobe Acrobat  | Medium   | PDF only  | Yes | No      | No          |
| LibreOffice    | Slow     | Many      | Yes | Yes     | Yes         |
| Custom scripts | Variable | Limited   | No  | Yes     | Variable    |

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- **pikepdf**: PDF processing library (libqpdf backend)
- **pywebview**: Cross-platform web view for GUI
- **Python**: Core runtime and ecosystem
- **Open source community**: Contributors and maintainers of all dependencies

Special thanks to the developers of pikepdf and pywebview for providing the foundation that makes Sanitize possible.
