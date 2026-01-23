# 🎨 Landing Page Design System

## Color Palette

### Primary Colors
- **Blue 600** (#0284c7) - Primary CTA buttons, links
- **Blue 700** (#0369a1) - Hover states
- **Blue 50** (#f0f9ff) - Light backgrounds
- **Blue 100** (#e0f2fe) - Subtle highlights

### Neutral Colors
- **Gray 900** (#111827) - Headings
- **Gray 800** (#1f2937) - Body text
- **Gray 600** (#4b5563) - Secondary text
- **Gray 300** (#d1d5db) - Borders
- **Gray 50** (#f9fafb) - Alternate sections

### Semantic Colors
- **Red 50-600** - Problem section
- **Green 50-500** - Success states
- **White** (#ffffff) - Main backgrounds

## Typography

### Headlines
- **H1**: 4xl (36px) mobile / 6xl (60px) desktop
  - Font weight: Bold (700)
  - Line height: Tight (1.2)
  
- **H2**: 3xl (30px) mobile / 4xl (36px) desktop
  - Font weight: Bold (700)
  - Margin bottom: 1.5rem

- **H3**: xl (20px) / 2xl (24px)
  - Font weight: Bold (700)

### Body Text
- **Large**: xl (20px) / 2xl (24px)
  - Used for: Subheadlines, important descriptions
  
- **Regular**: base (16px) / lg (18px)
  - Line height: 1.6
  - Used for: Body text, descriptions

- **Small**: sm (14px)
  - Used for: Secondary information

## Spacing

### Section Spacing
- **Vertical padding**: 4rem (64px) mobile / 6rem (96px) desktop
- **Container max-width**: 1152px (6xl)
- **Horizontal padding**: 1rem (16px)

### Component Spacing
- **Between sections**: 4-6rem
- **Between elements**: 1-2rem
- **Between cards**: 1.5-2rem

## Components

### Buttons

#### Primary Button
```
Background: Blue 600
Hover: Blue 700
Text: White
Padding: 2rem vertical, 2rem horizontal
Border radius: 0.5rem (8px)
Shadow: Medium on default, Large on hover
```

#### Secondary Button
```
Background: Transparent
Border: 2px Blue 600
Text: Blue 600
Hover background: Blue 50
Padding: 2rem vertical, 2rem horizontal
Border radius: 0.5rem (8px)
```

### Cards

#### Problem Card
```
Background: Red 50
Border: 1px Red 100
Padding: 1.5rem
Border radius: 0.5rem
Hover: None (static)
```

#### Solution Card
```
Background: White
Border: 2px Blue 100
Padding: 1.5rem
Border radius: 0.5rem
Hover: Border Blue 500
Transition: 200ms
```

#### Pricing Card
```
Background: White
Border: 2px Gray 200
Padding: 2rem
Border radius: 0.75rem (12px)
Hover: Border Blue 500, Shadow Large
Transition: 200ms
```

### Input Fields

```
Border: 2px Gray 300
Focus border: Blue 600
Padding: 1rem vertical, 1.5rem horizontal
Border radius: 0.5rem
Font size: lg (18px)
```

## Layout Structure

### Hero Section
```
Background: Gray 50
Padding: 5rem top, 4rem bottom (mobile)
         8rem top, 6rem bottom (desktop)
Text align: Center
Max width: 1152px
```

### Content Sections
```
Alternating backgrounds: White / Gray 50
Padding: 4rem vertical (mobile)
         6rem vertical (desktop)
Max width: 1152px
```

### Grid Layouts
```
Mobile: 1 column
Tablet (md): 2 columns
Desktop (lg): 3-4 columns
Gap: 1.5rem (24px)
```

## Icons

### Style
- Outline style (stroke, not fill)
- Stroke width: 2px
- Size: 3rem (48px) for large icons
       1.25rem (20px) for small icons

### Colors
- Primary icons: Blue 600
- Problem icons: Red 600
- Success icons: Green 500
- Neutral icons: Gray 600

## Responsive Breakpoints

```
sm:  640px  (Small tablets)
md:  768px  (Tablets)
lg:  1024px (Desktops)
xl:  1280px (Large desktops)
```

## Animation & Transitions

### Hover Effects
- Duration: 200ms
- Easing: Default (ease)

### Scroll Behavior
- Smooth scrolling enabled
- No jarring jumps

### Interactive Elements
- Buttons: Scale slightly on hover (optional)
- Cards: Border color change + shadow
- Links: Underline on hover

## Best Practices

### DO
✅ Use consistent spacing (multiples of 4px/8px)
✅ Maintain proper contrast ratios (WCAG AA)
✅ Keep mobile-first approach
✅ Use semantic HTML
✅ Provide hover states for interactive elements

### DON'T
❌ Mix different button styles in the same context
❌ Use more than 2-3 font sizes per section
❌ Overuse animations
❌ Forget focus states for accessibility
❌ Use pure black (#000000)

## Accessibility

- All interactive elements keyboard accessible
- Color contrast meets WCAG AA standards
- Focus states visible and clear
- Semantic HTML structure
- Alt text for images/icons (when needed)

## Performance

- No external dependencies beyond Tailwind
- Minimal JavaScript
- Static page generation
- Fast Time to Interactive (TTI)
- Optimized for Core Web Vitals
