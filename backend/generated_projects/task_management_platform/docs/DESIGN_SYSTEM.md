# Design System

Generated: 2026-01-13T22:28:51.613496

## Design Specifications

{
  "framework": "Next.js 14 + Tailwind CSS 3",
  "theme": "light",
  "component_library": "shadcn/ui",
  "design_system": {
    "typography": {
      "heading_1": "Inter, 32px, bold, 1.2",
      "heading_2": "Inter, 24px, semibold, 1.3",
      "body": "Inter, 16px, regular, 1.6",
      "caption": "Inter, 12px, regular, 1.4"
    },
    "colors": {
      "primary": "#3498db",
      "secondary": "#2ecc71",
      "accent": "#f1c40f",
      "success": "#2ecc71",
      "warning": "#f7dc6f",
      "error": "#e74c3c",
      "background": "#f9f9f9",
      "surface": "#f7f7f7",
      "border": "#ccc",
      "text_primary": "#333",
      "text_secondary": "#666"
    },
    "spacing": {
      "xs": "4px",
      "sm": "8px",
      "md": "16px",
      "lg": "24px",
      "xl": "32px"
    },
    "border_radius": {
      "sm": "4px",
      "md": "8px",
      "lg": "12px",
      "full": "9999px"
    },
    "shadows": {
      "sm": "0 1px 2px rgba(0,0,0,0.05)",
      "md": "0 4px 6px rgba(0,0,0,0.1)"
    }
  },
  "components": [
    {
      "name": "TeamCard",
      "variants": [
        "default",
        "selected"
      ],
      "states": [
        "active",
        "inactive"
      ],
      "sizes": [
        "sm",
        "md",
        "lg"
      ]
    },
    {
      "name": "TaskCard",
      "variants": [
        "default",
        "completed"
      ],
      "states": [
        "active",
        "overdue"
      ],
      "sizes": [
        "sm",
        "md",
        "lg"
      ]
    },
    {
      "name": "FileUpload",
      "variants": [
        "default",
        "drag-and-drop"
      ],
      "sizes": [
        "sm",
        "md",
        "lg"
      ]
    },
    {
      "name": "AnalyticsChart",
      "variants": [
        "default",
        "interactive"
      ],
      "sizes": [
        "sm",
        "md",
        "lg"
      ]
    },
    {
      "name": "Sidebar",
      "variants": [
        "default",
        "collapsed"
      ],
      "sizes": [
        "sm",
        "md",
        "lg"
      ]
    },
    {
      "name": "Modal",
      "variants": [
        "default",
        "fullscreen"
      ],
      "sizes": [
        "sm",
        "md",
        "lg"
      ]
    }
  ],
  "layout_patterns": {
    "teams": "sidebar navigation, team list, team details",
    "tasks": "task list, task details, team assignments",
    "files": "file list, file details, upload form",
    "analytics": "chart, filters, settings"
  },
  "inspiration": [
    "Trello",
    "Asana",
    "Slack"
  ],
  "accessibility": "WCAG 2.1 AA",
  "responsive_breakpoints": {
    "mobile": "320px - 640px",
    "tablet": "641px - 1024px",
    "desktop": "1025px+"
  }
}
