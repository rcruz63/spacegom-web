# Components

## Overview
The `components/` directory contains reusable HTML components used across the SpaceGOM application templates. These components provide consistent UI elements for dice rolling and result display.

## dice_result.html

### Purpose
`dice_result.html` is a reusable component for displaying dice roll results with animated visual feedback.

### Structure
- **Container**: Centered layout with pulse animation
- **Source Indicator**: Shows "USER INPUT" or "GENERATED" based on `is_manual` flag
- **Result Display**: Large, stylized number with glow effect
- **Details Section**: Optional additional information (conditional)

### Template Variables
- **`result`**: The numeric result to display (required)
- **`is_manual`**: Boolean indicating if result came from manual input
- **`details`**: Optional additional text information

### Styling
- **Animation**: Single pulse effect on load using CSS keyframes
- **Typography**: Orbitron font for result, tech-mono for details
- **Effects**: Drop shadow and scale transitions
- **Colors**: White text with gray accents

### Usage
```html
{% include 'components/dice_result.html' with result=7 is_manual=false details="2d6" %}
```

## dice_widget.html

### Purpose
`dice_widget.html` is a comprehensive dice rolling interface component that provides both automatic and manual dice rolling capabilities.

### Structure

#### Header
- **Title**: "DICE MODULE" with active status indicator
- **Status Badge**: Red "ACTIVE" indicator

#### Result Display Area
- **Default State**: "Ready to Roll" message with scanline effect
- **Dynamic Content**: HTMX target for roll results
- **Visual Effects**: Background patterns and hover states

#### Tab System
- **Auto Tab**: Automatic dice rolling interface
- **Manual Tab**: Physical dice input interface
- **Toggle Logic**: JavaScript-based tab switching

#### Auto Roll Form
- **Dice Count**: Number input (1-10 dice)
- **HTMX Integration**: Posts to `/api/roll-dice`
- **Styling**: Neon blue theme with hover effects

#### Manual Roll Form
- **Result Input**: Text field for physical dice totals
- **Hidden Fields**: Maintains API compatibility
- **Styling**: Neon green theme with hover effects

### Functionality

#### Auto Rolling
- **Input**: Number of d6 dice to roll
- **API Call**: POST to `/api/roll-dice` with `num_dices` parameter
- **Response**: Updates result area with roll outcome

#### Manual Input
- **Input**: Total value from physical dice
- **API Call**: POST to `/api/roll-dice` with `manual_result`
- **Response**: Logs and displays the entered result

### HTMX Integration
- **Target**: `#dice-result-area` for result display
- **Swap**: `innerHTML` to replace content
- **Progressive Enhancement**: Works without JavaScript

### Styling Features
- **Glass Panel**: Semi-transparent background with blur
- **Tech Borders**: Corner bracket decorations
- **Color Themes**: Blue for auto, green for manual
- **Hover Effects**: Shadow and opacity transitions
- **Scanline Effect**: Retro-tech visual element

### Dependencies
- **HTMX**: For dynamic form submission and content updates
- **TailwindCSS**: Utility classes for styling
- **Custom CSS**: Glass panel and tech border effects

### Integration Points
- **API Endpoint**: `/api/roll-dice` for processing rolls
- **Result Component**: Can display results using `dice_result.html`
- **Global Styling**: Inherits from base template styles

### Usage
```html
{% include 'components/dice_widget.html' %}
```

## Common Features

### Design Consistency
- **Space Theme**: Dark backgrounds with neon accents
- **Typography**: Orbitron for headers, tech-mono for data
- **Effects**: Glass panels, tech borders, glow effects
- **Animations**: Smooth transitions and hover states

### Accessibility
- **Labels**: Proper form labels for inputs
- **Keyboard Navigation**: Tab-based navigation support
- **Visual Feedback**: Clear state indicators and animations

### Performance
- **Lightweight**: Minimal HTML and CSS
- **Efficient Updates**: HTMX for partial page updates
- **No JavaScript Dependencies**: Progressive enhancement

### Maintenance
- **Modular**: Self-contained components
- **Reusable**: Can be included in multiple templates
- **Consistent**: Follows application design patterns