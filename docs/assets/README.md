# Assets Directory

This directory contains logo and favicon files for the BGSTM documentation site.

## Required Files

To complete the documentation site setup, add the following image files to this directory:

- **`logo.png`** - Site logo (recommended size: 192x192 pixels)
  - Displayed in the navigation header
  - Should represent the BGSTM project branding
  
- **`favicon.png`** - Site favicon (recommended size: 32x32 pixels)
  - Displayed in browser tabs and bookmarks
  - Should be a simplified version of the logo

## Placeholder Notice

Until these images are added, MkDocs Material will use default placeholder icons. The documentation site will still function normally, but custom branding will not be displayed.

## Adding Images

1. Create or obtain logo and favicon images following the recommended sizes
2. Save them in this directory as `logo.png` and `favicon.png`
3. Rebuild the documentation site with `mkdocs build` or `mkdocs serve`
4. The custom images will automatically be included in the site

## Image Guidelines

- Use PNG format for transparency support
- Ensure images are optimized for web use
- Logo should be clearly visible at small sizes
- Favicon should be simple and recognizable
- Consider both light and dark theme visibility
