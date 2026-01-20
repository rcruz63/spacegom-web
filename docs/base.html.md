# base.html

## Overview
`base.html` is the foundational template for the SpaceGOM Companion web application. It provides the core HTML structure, CSS styling, JavaScript utilities, and global navigation system used across all pages.

## Structure

### HTML Head
- **DOCTYPE**: HTML5 document declaration
- **Meta Tags**: UTF-8 charset, responsive viewport
- **Title**: "Spacegom Companion"
- **External Libraries**:
  - TailwindCSS (CDN)
  - HTMX (v1.9.10)
  - Google Fonts (Orbitron, Share Tech Mono)

### TailwindCSS Configuration
Custom theme extensions:
- **Font Families**:
  - `orbitron`: Sci-fi gaming font
  - `tech`: Monospace technical font
- **Color Palette**:
  - `space`: Dark space-themed colors (900, 800, 700)
  - `neon`: Bright accent colors (blue, green, red)

### Custom CSS Styles

#### Background
- Dark grid pattern background with neon blue accents
- 30px grid size with subtle transparency

#### Glass Panel Effect
- Semi-transparent background with backdrop blur
- Neon blue borders and subtle glow effects

#### Tech Border
- Corner brackets using CSS pseudo-elements
- Creates a technical/scientific interface aesthetic

#### Toast Notifications
- Fixed positioning in top-right corner
- Animated slide-in/slide-out effects
- Color-coded by type (success, error, info, warning)

#### Results Panel
- Slide-out panel from the right side
- 450px width with glass panel styling
- Smooth cubic-bezier transitions

## HTML Body Structure

### Header
- **Title**: "Spacegom Companion" with neon blue styling
- **Subtitle**: "SYSTEM ONLINE // CAPTAIN ACCESS GRANTED"
- **Game Date**: Displays current in-game date (hidden on mobile)

### Global Navigation Bar
Conditionally displayed when `game_id` parameter is present:
- **Navigation Tabs**: Dashboard, Personnel, Treasury, Trade, Missions, Logs
- **Game Info Bar**: Date, Planet, Balance, Expenses, Next Event
- **Advance Time Button**: Triggers time advancement with dice rolling

### Main Content Area
- Jinja2 block `{% block content %}` for page-specific content
- Responsive max-width container

### Footer
- Version information and security notice
- Centered, small text styling

## JavaScript Functions

### Toast System
- `showToast(message, type, duration)`: Displays temporary notifications
- Types: success (green), error (red), info (blue), warning (orange)
- Auto-removal after specified duration

### Results Panel
- `showResultsPanel(content)`: Displays content in slide-out panel
- `closeResultsPanel()`: Hides the results panel

### Hire Results Display
- `showHireResult(data)`: Shows detailed hiring attempt results
- Includes dice visualization, modifiers, success/failure states
- Handles next task initiation display

### Global Navigation
- `initGlobalNav()`: Initializes navigation based on game_id parameter
- `highlightActiveTab()`: Highlights current page in navigation
- `loadGlobalGameInfo(gameId)`: Fetches and displays game state information

### Time Advancement System
- `globalAdvanceTime()`: Shows dice mode selection modal
- `globalProceedWithDice(mode)`: Handles auto/manual dice selection
- `globalShowManualDice()`: Input form for physical dice results
- `globalExecuteTimeAdvance(manualDice)`: Processes time advancement API call

### Modal Systems
- **Salary Payment Modal**: Displays payroll information
- **Mission Deadline Modal**: Handles mission resolution choices
- `resolveMission(missionId, success, gameId)`: Processes mission outcomes

### Date Management
- `updateHeaderGameDate(gameId)`: Updates header date display
- Integrates with game state API

## Dependencies
- **dice-roller.js**: Universal dice rolling component
- **HTMX**: For dynamic content updates
- **TailwindCSS**: Utility-first CSS framework
- **Google Fonts**: Custom typography

## Integration Points
- **Jinja2 Templates**: Uses block inheritance pattern
- **URL Parameters**: game_id for navigation and API calls
- **API Endpoints**: Games, treasury, planets, time, missions
- **Global Functions**: Available to child templates and page scripts

## Responsive Design
- Mobile-first approach with responsive breakpoints
- Navigation adapts to screen size
- Touch-friendly button sizes and spacing

## Theme Consistency
- Dark space theme with neon accents
- Consistent use of Orbitron font for headings
- Tech-mono font for body text and data
- Glass panel effects throughout the interface

## Security Notes
- Client-side game state validation
- Secure API communication patterns
- Input sanitization for manual dice entry