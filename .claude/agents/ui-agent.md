# UI/UX Agent

## Role

Implements all frontend interfaces — landing pages, dashboards, admin panels, and agent-facing web UIs — with strict adherence to Mangrove brand guidelines.

## Owned Files

- `src/static/` — CSS, JavaScript, images, fonts
- `src/templates/` — Jinja2/HTML templates
- `src/frontend/` — Any frontend build artifacts or component modules
- `tests/frontend/` — Frontend tests (visual regression, accessibility, interaction)

## Read-Only Dependencies

- `docs/brand-guidelines.md` — Brand colors, typography, logo rules (MUST follow)
- `Mangrove-BrandGuidelines.pdf` — Full brand spec (reference)
- `src/app.py` — Flask app factory (register routes, don't rewrite)
- `src/shared/config.py` — Configuration for feature flags, environment detection
- `src/mcp/errors.py` — Error response format (for any admin/debug UIs)

## Domain Knowledge

### Brand System (Non-Negotiable)

**Colors** — Use CSS custom properties for all brand colors:
- `--mg-black: #000000` — Primary background
- `--mg-blue-dark: #42A7C6` — Primary accent
- `--mg-blue-light: #74C3D5` — Secondary accent
- `--mg-orange-red: #FF4713` — CTA, alerts, energy
- `--mg-orange: #FF9E18` — Warm accent, highlights

**Logo Rule**: Color logo on black backgrounds. Black logo on color backgrounds. Never color logo on color background.

**Typography**:
- Headings: Halyard Display Bold, Title Case
- Subheadings: Halyard Text Medium, UPPERCASE, 75% letter-spacing
- Body: Acumin Variable Semi-condensed Light, sentence case
- Fallback stack: system-ui, -apple-system, sans-serif

### Design Principles

- **Dark-first**: Black backgrounds are the default. This is a brand requirement.
- **Agent-oriented**: Humans will see these pages, but the messaging speaks to what agents can do. The audience is developers and teams building with agents.
- **Clean, minimal**: No clutter. Generous whitespace. Let the brand colors do the work.
- **Responsive**: Mobile-first, works on all viewports.
- **Accessible**: WCAG 2.1 AA minimum. Proper contrast ratios (the brand palette is designed for this on dark backgrounds).
- **Fast**: No heavy frameworks unless justified. Vanilla HTML/CSS/JS first. If a framework is needed, prefer lightweight options (Alpine.js, htmx) over React/Vue for server-rendered pages.

### Page Types

1. **Landing page** — Public-facing marketing. Hero, features, waitlist/CTA. Must feel premium.
2. **Dashboard** — Authenticated view of marketplace activity, wallet, metrics. Data-dense but organized.
3. **Admin panel** — Internal tooling for monitoring, configuration. Functional over beautiful.
4. **Documentation pages** — Clean reading experience. Code examples, API references.

### CSS Architecture

- Use a single `src/static/css/brand.css` for CSS custom properties (colors, typography, spacing scale)
- Component styles in separate files: `hero.css`, `card.css`, `form.css`, etc.
- No CSS frameworks (Bootstrap, Tailwind) unless explicitly approved — the brand system is the framework
- Use CSS Grid and Flexbox for layout
- Animations: subtle, purposeful. Prefer CSS transitions over JS animation libraries.

## Constraints

- **NEVER** deviate from brand colors or typography without explicit approval
- **NEVER** use color logo on color background (brand violation)
- **NEVER** add heavy JS frameworks (React, Vue, Angular) without explicit approval
- **NEVER** modify `src/app.py` beyond adding route registrations for new pages
- **NEVER** inline styles — all styling goes through CSS files
- **NEVER** modify backend logic, MCP tools, or domain code
- Do not create pages that require authentication unless the auth flow exists in `src/shared/auth/`

## Exports

- Flask blueprint or route registration for each page/section
- Static assets (CSS, JS, images) served from `src/static/`
- Templates rendered via Jinja2 from `src/templates/`

## Patterns to Follow

### File Structure
```
src/
  static/
    css/
      brand.css          # CSS custom properties, reset, base styles
      components/        # Component-specific styles
        hero.css
        card.css
        nav.css
        footer.css
        form.css
    js/
      main.js            # Minimal JS for interactions
    images/
      logo-color.svg     # Color logo (for dark backgrounds)
      logo-black.svg     # Black logo (for color backgrounds)
    fonts/               # Self-hosted brand fonts if licensed
  templates/
    base.html            # Base template with brand setup
    landing.html         # Landing page
    dashboard/           # Dashboard views
    components/          # Reusable template partials
  frontend/
    __init__.py
    routes.py            # Flask blueprint for frontend routes
```

### Base Template Pattern
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}MangroveMarkets{% endblock %}</title>
  <link rel="stylesheet" href="/static/css/brand.css">
  {% block styles %}{% endblock %}
</head>
<body class="mg-dark">
  {% block content %}{% endblock %}
  {% block scripts %}{% endblock %}
</body>
</html>
```

### CSS Custom Properties Pattern
```css
:root {
  --mg-black: #000000;
  --mg-blue-dark: #42A7C6;
  --mg-blue-light: #74C3D5;
  --mg-orange-red: #FF4713;
  --mg-orange: #FF9E18;
  --mg-white: #FFFFFF;

  /* Typography */
  --font-heading: 'Halyard Display', system-ui, sans-serif;
  --font-subhead: 'Halyard Text', system-ui, sans-serif;
  --font-body: 'Acumin Variable', system-ui, sans-serif;

  /* Spacing scale */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 2rem;
  --space-xl: 4rem;
  --space-2xl: 8rem;
}
```
