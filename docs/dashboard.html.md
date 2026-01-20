# dashboard.html

## Overview
`dashboard.html` is the main game interface template for the SpaceGOM Companion application. It extends `base.html` and provides a comprehensive command center with ship status, navigation controls, planet exploration, and game management features.

## Structure

### Template Inheritance
- **Extends**: `base.html`
- **Block**: `content` - Contains the main dashboard interface

### Custom CSS Styles

#### Star Background
- Radial gradient pattern simulating starfield
- Multiple positioned star elements for depth
- Used in quadrant navigation area

#### Location Button Styling
- Active state with neon green accents
- Hover effects for interactive elements

## Main Layout

### Company Header
- **Company Name**: Displays current company name
- **Game ID**: Shows unique game identifier
- **Ship Information**: Name and model of command ship

### Critical Status HUD
Glass panel containing essential ship metrics:
- **Fuel Level**: Visual bar (0-30 units) with color coding
- **Storage Capacity**: UCN storage with dynamic maximum
- **Damage System**: Toggleable damage states (Light/Moderate/Severe)
- **Critical Alert**: Shows when hyperspace drive is destroyed

### Calendar and Reputation Panel
- **Game Date**: Day/Month/Year display
- **Reputation**: Adjustable -5 to +5 scale with color coding
- **Treasury**: Current Space Credits balance
- **Monthly Expenses**: Salary and loan payments

### Navigation Grid System

#### Area Navigation
- **Area Display**: Current area number (2-12)
- **Navigation Buttons**: Previous/Next area controls
- **Ship Stats**: Jump range and position badges

#### Quadrant Grid
- **6x6 Grid**: Representing current area quadrants
- **Coordinate System**: A-F columns, 1-6 rows
- **Fog of War**: Initially obscured quadrants
- **Ship Position**: Animated ship icon with glow effect
- **Planet Codes**: Revealed planet identifiers

#### Location Controls
Five location states on planets:
- **Mundo**: Planetary surface
- **Espaciopuerto**: Spaceport facilities
- **Instalación**: Orbital installations
- **En ruta**: In transit
- **Estación**: Space stations

### Planet Information Panel
Expandable panel showing detailed planet data:
- **Basic Info**: Name, code, life support, tech level
- **Risk Factors**: Contagion risk, legal order threshold
- **Trade Data**: Self-sufficiency, UCN per order, max passengers
- **Facilities**: Spaceport details, orbital installations
- **Products**: Available trade goods with color coding

### Stellar Archives
- **World Log**: Discovered planets with coordinates
- **Area Planets**: Current area planet list with details

### Passenger Transport Widget
- **Capacity Display**: Ship and planet passenger limits
- **Active Modifiers**: Current bonuses/penalties
- **Transport Button**: Initiates passenger boarding action

## JavaScript Functionality

### Game State Management
- **gameState Object**: Central state storage for UI
- **Initialization**: Loads from API on page load
- **Real-time Updates**: Dynamic UI updates from state changes

### Ship Status Controls
- **Fuel Adjustment**: Increment/decrement with visual feedback
- **Storage Management**: Dynamic capacity updates
- **Damage Tracking**: Visual damage state toggles
- **Reputation System**: Color-coded reputation display

### Navigation System
- **Area Navigation**: API-driven area changes
- **Quadrant Exploration**: Fog removal and planet discovery
- **Ship Positioning**: Visual ship movement on grid
- **Location Updates**: Planetary position state management

### Planet Interaction
- **Planet Details**: Comprehensive planet information loading
- **Information Display**: Formatted data presentation
- **Product Visualization**: Color-coded trade goods
- **Facility Indicators**: Orbital installation badges

### Data Loading Functions
- **Treasury Data**: Balance and expense information
- **World Log Updates**: Discovered planet tracking
- **Area Data Loading**: Planet lists for current area
- **Header Updates**: Global navigation synchronization

## Key Features

### Visual Design
- **Space Theme**: Dark backgrounds with neon accents
- **Glass Panels**: Semi-transparent UI elements
- **Tech Borders**: Corner bracket decorations
- **Responsive Grid**: Mobile-adaptive layouts

### Interactive Elements
- **Hover Effects**: Button and panel highlighting
- **Click Handlers**: Quadrant selection and planet details
- **Animation**: Smooth transitions and state changes
- **Toast Notifications**: User feedback system

### Data Integration
- **API Endpoints**: Games, planets, treasury, navigation
- **State Persistence**: Server-side game state management
- **Real-time Updates**: Dynamic content loading
- **Error Handling**: Graceful failure management

## Dependencies
- **base.html**: Template inheritance and global functions
- **passenger_transport.js**: Transport action handling
- **HTMX**: Dynamic content updates (inherited)
- **TailwindCSS**: Styling framework (inherited)

## Integration Points
- **Global Navigation**: Inherited from base.html
- **Toast System**: Uses global notification functions
- **Dice Roller**: Integrated transport mechanics
- **Time Advancement**: Global time control integration

## Performance Considerations
- **Lazy Loading**: Planet details loaded on demand
- **Efficient Updates**: Targeted DOM manipulation
- **Memory Management**: State object for UI synchronization
- **API Optimization**: Batched data loading where possible