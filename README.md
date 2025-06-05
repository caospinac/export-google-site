# Google Sites PDF Exporter

Script to automatically export all pages from a Google Site to individual PDF files, maintaining the site's hierarchical structure in the filenames.

## Features

- Exports all pages from a Google Site to PDF
- Uses URL structure for descriptive filenames
- Cookie management for automatic authentication
- Headless browser (no GUI) for better performance
- Uses Chrome included with Playwright

## Requirements

- Python 3.7+
- Google Chrome installed
- Internet connection

## Installation

### 1. Clone or download the script

```bash
git clone <repository-url>
cd scripts/sites
```

### 2. Create virtual environment (recommended)

```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate     # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
playwright install chrome
```

## Cookie Configuration (Optional but Recommended)

To avoid having to authenticate manually each time:

### 1. Export cookies from Chrome

1. Install an extension like "Get cookies.txt" or "Cookie Editor"
2. Go to the Google Site you want to export
3. Log in normally
4. Export the cookies in JSON format
5. Save the file as `cookies.json` in the same directory as the script

### 2. cookies.json file format

```json
[
  {
    "name": "cookie_name",
    "value": "cookie_value",
    "domain": ".google.com",
    "path": "/",
    "secure": true,
    "httpOnly": false,
    "expirationDate": 1234567890
  }
]
```

## Usage

### Basic command

```bash
python export_google_site.py --url "https://sites.google.com/your-domain/your-site"
```

### Complete example

```bash
python export_google_site.py --url "https://sites.google.com/company.com/knowledge-base"
```

## Generated File Structure

The script creates filenames based on URL structure:

- URL: `https://sites.google.com/domain/site/section/page`
- File: `section_page.pdf`

### Examples:

| Original URL | Generated File |
|-------------|----------------|
| `/knowledge-base/getting-started` | `getting_started.pdf` |
| `/knowledge-base/user-guide/setup` | `user_guide_setup.pdf` |
| `/knowledge-base/admin/permissions` | `admin_permissions.pdf` |

## Project Structure

```
sites/
├── export_google_site.py    # Main script
├── requirements.txt         # Python dependencies
├── cookies.json            # Authentication cookies (optional)
├── README.md              # This file
└── google_site_export/    # Output directory (created automatically)
    ├── getting_started.pdf
    ├── user_guide.pdf
    └── ...
```

## Troubleshooting

### Error: "Executable doesn't exist"

```bash
playwright install chrome
```

### Authentication error

1. Verify that the `cookies.json` file exists and has the correct format
2. Make sure the cookies haven't expired
3. Re-export cookies from your browser

### Pages not found

The script searches for navigation links using various CSS selectors. If it doesn't find pages:

1. Verify that the site has a visible navigation menu
2. Check the site's HTML structure
3. Modify the selectors in the code if necessary

### Timeout on slow pages

The script waits 10 seconds per page. For slow sites, modify the timeout:

```python
page.wait_for_load_state("networkidle", timeout=20000)  # 20 seconds
```

## Customization

### Change output format

Modify the `page.pdf()` function to change format, margins, etc:

```python
page.pdf(
    path=pdf_path,
    format="A4",           # A4, Letter, Legal, etc.
    print_background=True,
    margin={
        "top": "2cm",
        "bottom": "2cm", 
        "left": "2cm",
        "right": "2cm"
    }
)
```

### Change navigation selectors

Modify the `selectors` list in the code to adapt to different site structures:

```python
selectors = [
    "nav ul li a",              # Standard navigation
    "[role='navigation'] a",    # ARIA navigation
    ".custom-menu a",           # Custom selector
]
```

## Dependencies

- **playwright**: Browser automation
- **python-slugify**: Filename sanitization

## License

MIT License - Free for personal and commercial use.

## Contributing

Contributions are welcome. Please:

1. Fork the project
2. Create a branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## Support

To report bugs or request features, open an issue in the repository.
