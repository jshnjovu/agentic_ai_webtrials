# Website Template Generator - Frontend

This is the frontend implementation of the Website Template Generator system, designed to create professional websites quickly using pre-built templates and business data input.

## Features

### 🎨 Template System
- **Base Template**: Extensible foundation for all website templates
- **Restaurant Templates**: Specialized for food service businesses
- **Retail Templates**: Optimized for e-commerce and retail stores
- **Service Templates**: Professional service business layouts
- **Professional Templates**: Corporate and consulting business designs

### 🚀 User Experience
- **Template Gallery**: Browse and select from available templates
- **Progressive Forms**: Step-by-step business data collection
- **Live Preview**: See your website before generation
- **Mobile-First Design**: Responsive across all devices
- **Accessibility**: WCAG 2.1 AA compliant

### 🎯 Design System
- **Custom Color Palette**: Professional business-focused colors
- **Typography**: Inter + Source Sans Pro + JetBrains Mono
- **Component Library**: Reusable UI components
- **Responsive Grid**: Mobile-first responsive design
- **Animation**: Smooth transitions and micro-interactions

## Project Structure

```
frontend/
├── components/           # React components
│   ├── TemplateGallery.tsx      # Template selection interface
│   └── BusinessDataForm.tsx     # Progressive business data form
├── templates/            # Website templates
│   ├── base/            # Base template foundation
│   │   └── index.tsx    # BaseTemplate component
│   └── themes/          # Template variations
│       ├── restaurant/  # Restaurant-specific templates
│       └── retail/      # Retail-specific templates
├── pages/               # Next.js pages
│   ├── _app.tsx         # App wrapper
│   └── templates.tsx    # Main template dashboard
├── styles/              # Global styles
│   └── globals.css      # Tailwind + custom styles
├── utils/               # Utility functions
│   └── cn.ts            # Class name utility
└── package.json         # Dependencies
```

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Open [http://localhost:3000/templates](http://localhost:3000/templates)

### Build for Production

```bash
npm run build
npm start
```

## Template Development

### Creating New Templates

1. **Extend BaseTemplate**: All templates should extend the base template
2. **Follow Naming Convention**: Use descriptive names (e.g., `ModernRestaurantTemplate`)
3. **Implement Required Props**: Include all necessary business data fields
4. **Mobile-First Design**: Ensure responsive behavior across breakpoints

### Example Template Structure

```tsx
import React from 'react';
import { BaseTemplate, BaseTemplateProps } from '../base';

export interface CustomTemplateProps extends BaseTemplateProps {
  // Add custom props here
  customField?: string;
}

export const CustomTemplate: React.FC<CustomTemplateProps> = ({
  customField,
  ...baseProps
}) => {
  return (
    <BaseTemplate {...baseProps}>
      {/* Your custom template content */}
    </BaseTemplate>
  );
};
```

## Design System

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | #2563EB | Main brand color, buttons, links |
| Secondary | #64748B | Secondary actions, borders |
| Accent | #F59E0B | Call-to-action, highlights |
| Success | #10B981 | Positive feedback, confirmations |
| Error | #EF4444 | Errors, destructive actions |

### Typography

- **Primary**: Inter (sans-serif) - Body text, UI elements
- **Headings**: Source Sans Pro (sans-serif) - Titles, headings
- **Monospace**: JetBrains Mono - Code, technical content

### Breakpoints

- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px+

## Component API

### TemplateGallery

```tsx
<TemplateGallery
  templates={templates}
  onTemplateSelect={handleSelect}
  selectedTemplate={selected}
/>
```

### BusinessDataForm

```tsx
<BusinessDataForm
  initialData={data}
  onDataChange={handleChange}
  templateCategory="restaurant"
/>
```

### BaseTemplate

```tsx
<BaseTemplate
  businessName="Business Name"
  tagline="Business Tagline"
  description="Business Description"
  phone="(555) 123-4567"
  email="contact@business.com"
  address="123 Business St"
  services={["Service 1", "Service 2"]}
>
  {/* Custom content */}
</BaseTemplate>
```

## Accessibility Features

- **Semantic HTML**: Proper heading hierarchy and landmarks
- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: WCAG 2.1 AA compliant
- **Focus Management**: Clear focus indicators

## Performance Optimizations

- **Lazy Loading**: Components load on demand
- **Image Optimization**: Responsive images with Next.js
- **CSS Optimization**: Tailwind CSS with PurgeCSS
- **Bundle Splitting**: Code splitting for better performance

## Testing

```bash
# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run linting
npm run lint
```

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository
2. Configure build settings
3. Deploy automatically on push

### Manual Deployment

1. Build the project: `npm run build`
2. Export static files: `npm run export`
3. Deploy to your hosting provider

## Contributing

1. Follow the established code style
2. Add tests for new components
3. Update documentation
4. Ensure accessibility compliance
5. Test across different devices and browsers

## License

This project is part of the Business Lead Generation System.

## Support

For questions or issues, please refer to the project documentation or create an issue in the repository.
