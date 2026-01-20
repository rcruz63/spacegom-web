# passenger_transport.js

## Overview
`passenger_transport.js` is a JavaScript module that handles the passenger transport action in the SpaceGOM game. It provides a complete UI workflow for rolling dice to determine passenger influx, executing the transport action via API, and displaying results in a modal interface.

## Dependencies
- `DiceRollerUI` - Universal dice rolling component
- HTMX for dynamic content updates
- TailwindCSS for styling
- Custom CSS classes (neon-green, space-800, etc.)

## Key Functions

### `init()`
Initializes the passenger transport functionality by:
- Setting up event listeners for the transport button
- Loading initial transport information from the server
- Configuring the UI state

### `loadInfo()`
Fetches current transport information from the API endpoint `/api/games/{gameId}/passenger-transport/info` and updates the UI with:
- Available ships and their capacities
- Current personnel assignments
- Transport modifiers

### `refreshInfo()`
Refreshes the transport information and updates the UI state, particularly useful after actions that might change personnel or ship availability.

### `startTransport()`
Initiates the passenger transport action by:
- Retrieving current transport information
- Setting up dice roll modifiers (manager bonus)
- Requesting a 2d6 dice roll through DiceRollerUI

### `executeAction(diceResult)`
Executes the transport action via API call to `/api/games/{gameId}/passenger-transport/execute` with:
- Manual dice results if provided
- Processes the server response and displays results

### `showResultModal(result)`
Displays a comprehensive results modal showing:
- Dice roll visualization
- Passenger boarding numbers
- Revenue breakdown
- Personnel updates (moral/experience changes)
- Formatted with custom styling and animations

## UI Components

### Transport Button
- Dynamically enabled/disabled based on available ships
- Shows ship count and capacity information
- Triggers the transport workflow

### Results Modal
- Persistent modal with glass-panel styling
- Displays dice results, passenger counts, and revenue
- Includes personnel update notifications
- Animated entry/exit with backdrop blur

## Data Flow
1. User clicks transport button
2. System loads current transport info
3. Dice roll is requested (2d6 + modifiers)
4. Roll result is sent to server for processing
5. Server calculates passengers, revenue, and personnel changes
6. Results are displayed in a modal
7. UI refreshes and page reloads after modal close

## Error Handling
- Network errors are caught and displayed via toast notifications
- API errors show server-provided error messages
- Modal creation handles existing modal cleanup

## Styling Notes
- Uses custom font-orbitron for headers
- Neon-green accents for success states
- Space-themed color palette (space-800, space-900)
- Responsive grid layouts for result display
- Shadow effects and border animations

## Integration Points
- Depends on global `showToast` function for notifications
- Integrates with DiceRollerUI for dice rolling interface
- Uses HTMX for potential dynamic updates (though not heavily utilized here)
- Relies on URL parameters for game_id extraction