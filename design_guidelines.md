# PsyAI Platform Design Guidelines

## Design Approach
**Reference-Based Approach**: Medical/Healthcare platforms like Headspace Health, BetterHelp, and Teladoc Health for professional therapeutic interfaces, combined with modern productivity tools like Linear and Notion for expert dashboards.

**Key Design Principles**:
- Clinical professionalism with approachable warmth
- Clear visual hierarchy for critical medical information
- Trust-building through clean, uncluttered interfaces
- Accessibility-first design for diverse user needs

## Core Design Elements

### A. Color Palette
**Primary Colors**:
- Light mode: Deep medical blue (210 85% 25%) for trust and professionalism
- Dark mode: Soft medical blue (210 60% 85%) for reduced eye strain
- Success states: Calming green (150 60% 45%) for positive outcomes
- Warning states: Warm amber (35 80% 55%) for attention without alarm
- Error states: Gentle red (350 65% 50%) for critical issues

**Background Colors**:
- Light mode: Clean white with subtle blue-gray tints (210 15% 97%)
- Dark mode: Deep navy backgrounds (210 25% 8%) for comfort

### B. Typography
- **Primary**: Inter via Google Fonts for excellent readability
- **Secondary**: Source Sans Pro for body text in clinical contexts
- **Hierarchy**: Large headings (2xl-4xl), readable body text (base-lg), small annotations (sm)

### C. Layout System
**Spacing Primitives**: Tailwind units of 4, 6, 8, and 12
- Consistent 4-unit gaps between related elements
- 6-unit spacing for section separation
- 8-unit margins for component boundaries
- 12-unit spacing for major layout sections

### D. Component Library
**Chat Interface**:
- Patient messages: Light blue bubbles with rounded corners
- AI responses: White/gray bubbles with subtle medical iconography
- Expert annotations: Highlighted yellow overlays with clear attribution

**Expert Dashboard**:
- Card-based case reviews with confidence score indicators
- Color-coded priority levels (green/amber/red)
- Clean data tables with sortable columns
- Modal overlays for detailed case examination

**Navigation**:
- Clean sidebar navigation with medical icons
- Breadcrumb trails for complex workflows
- Tab-based interfaces for multi-step processes

**Data Visualization**:
- Simple progress bars for confidence scores
- Timeline views for conversation history
- Minimal charts using medical color palette

### E. Visual Treatments
**Gradients**: Subtle blue-to-white gradients in hero sections and cards
**Shadows**: Soft, medical-grade shadows (not harsh black)
**Borders**: Thin, professional borders using primary color at low opacity
**Iconography**: Heroicons for consistency, medical-specific icons via Font Awesome

## Images
**No large hero images** - this is a professional medical platform focused on functionality over marketing appeal. Use small, supportive icons and illustrations:
- Medical professional illustrations in dashboard headers
- Simple iconography for different user types (patient/expert/AI)
- Subtle background patterns in empty states

## Key Interface Specifications
- **Patient Chat**: Full-height chat interface with fixed input bar
- **Expert Dashboard**: Multi-panel layout with case queue, active review, and history
- **Confidence Indicators**: Clear visual meters showing AI certainty levels
- **Review Overlays**: Modal interfaces for expert feedback with annotation tools
- **Responsive Design**: Mobile-first approach with collapsible sidebars

## Accessibility & Medical Compliance
- High contrast ratios for all text (WCAG AAA)
- Keyboard navigation for all interactive elements
- Screen reader optimization for medical terminology
- Color-blind friendly indicators (not relying solely on color)
- Large touch targets for mobile medical professionals