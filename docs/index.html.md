# index.html

## Overview
`index.html` is the landing page template for the SpaceGOM Companion application. It extends `base.html` and serves as the main entry point, displaying game statistics, saved games list, and navigation options for starting or continuing games.

## Structure

### Template Inheritance
- **Extends**: `base.html`
- **Block**: `content` - Contains the main landing interface

## Main Layout

### Command Center Section
Full-width glass panel containing:
- **Welcome Message**: Sci-fi themed greeting
- **Navigation Buttons**:
  - **New Game**: Links to `/setup` for game creation
  - **Continue Last**: Loads most recent saved game (disabled if no games)

### Games Summary Statistics
Grid displaying key metrics:
- **Total Games**: Count of all saved games
- **Active Games**: Currently playable games
- **Last Activity**: Time since last game interaction
- **Areas Explored**: Unique areas discovered across all games

### Saved Games List Panel
- **Title**: "PARTIDAS GUARDADAS" with folder icon
- **Scrollable List**: Game cards with click-to-load functionality
- **Empty State**: Message when no games exist

### System Information Panel
- **Title**: "INFORMACIÓN DEL SISTEMA" with info icon
- **System Stats**:
  - Version information
  - Database planet count
  - Available areas range
  - System status indicator
- **Update Log**: Recent changes and improvements

## JavaScript Functionality

### Game Loading System
- **`loadGames()`**: Fetches all games from `/api/games` endpoint
- **Statistics Calculation**: Computes totals and unique areas
- **Activity Tracking**: Calculates time since last game update
- **UI Updates**: Populates stats and games list

### Game Card Creation
- **`createGameCard(game)`**: Generates interactive game cards
- **Information Display**:
  - Company/ship names
  - Last update timestamp
  - Area, density, and ship model badges
- **Click Handler**: Navigates to dashboard with game_id

### Continue Functionality
- **`continueLastGame()`**: Loads most recent game automatically
- **Sorting Logic**: Finds game with latest `updated_at` timestamp
- **Navigation**: Redirects to dashboard with selected game

### Initialization
- **`window.onload`**: Triggers game loading on page load
- **Error Handling**: Graceful failure with error messages

## Key Features

### Visual Design
- **Space Theme**: Consistent with application aesthetic
- **Glass Panels**: Semi-transparent UI containers
- **Tech Borders**: Corner bracket decorations
- **Responsive Layout**: Mobile-adaptive grid system

### Interactive Elements
- **Hover Effects**: Button and card highlighting
- **Click Navigation**: Direct game loading
- **Dynamic Content**: Real-time statistics updates
- **Loading States**: User feedback during data fetching

### Data Presentation
- **Time Formatting**: Relative time display (minutes/hours/days)
- **Badge System**: Color-coded game attributes
- **Scrollable Lists**: Efficient space usage for multiple games
- **Empty States**: Helpful messaging for new users

## Dependencies
- **base.html**: Template inheritance and global styling
- **API Endpoints**: `/api/games` for game data retrieval
- **Navigation**: Links to `/setup` and `/dashboard`

## Integration Points
- **Global Navigation**: Inherited from base.html (hidden on index)
- **Game Creation**: Links to setup workflow
- **Game Continuation**: Direct dashboard access with game_id
- **Time Formatting**: Localized Spanish date formatting

## User Experience
- **Quick Access**: Continue button for returning players
- **Overview**: Statistics provide game progress insight
- **Discovery**: System information educates new users
- **Performance**: Efficient loading and minimal API calls

## Error Handling
- **Network Errors**: Console logging and user feedback
- **Empty States**: Helpful messages for no games scenario
- **Loading States**: Prevents interaction during data fetch
- **Graceful Degradation**: Functional even with partial data failure