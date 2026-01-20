# personnel.html

## Overview
`personnel.html` is the personnel management interface for the SpaceGOM Companion application. It extends `base.html` and provides comprehensive functionality for viewing, hiring, and managing company personnel.

## Structure

### Template Inheritance
- **Extends**: `base.html`
- **Block**: `content` - Contains the personnel management interface

### Header Section
- **Title**: "GESTIÓN DE PERSONAL" with neon blue styling
- **Game Info**: Displays current game ID and date
- **Navigation**: Back to dashboard link

### Summary Cards
Grid displaying key personnel metrics:
- **Total Personnel**: Count of active employees
- **Monthly Salaries**: Total salary expenditure
- **Pending Tasks**: Director's task queue count
- **Next Event**: Upcoming game event date

### Actions Bar
- **Hire Button**: Initiates new personnel search process

### Director's Task Queue
Conditional section showing director's active and pending tasks:
- **Current Task**: Active hiring process with completion date
- **Pending Tasks**: Queued hiring requests with management options
- **Task Management**: Delete pending tasks functionality

### Personnel Table
Comprehensive employee listing with:
- **ID**: Unique employee identifier
- **Name**: Employee name
- **Position**: Job title/role
- **Salary**: Monthly salary in Space Credits
- **Experience**: Novato/Estándar/Veterano with color coding
- **Morale**: Baja/Media/Alta with color coding

## Hire Modal System

### Position Selection
- **Dropdown**: Available positions loaded from API
- **Position Details**: Search time, base salary, hire threshold, tech level
- **Dynamic Updates**: Details update on position selection

### Experience Level Selection
Three-tier system with visual buttons:
- **Novato**: 50% time, 50% salary, green theme
- **Estándar**: 100% time, 100% salary, blue theme (default)
- **Veterano**: 200% time, 200% salary, purple theme

### Hire Summary
Dynamic calculation display:
- **Estimated Days**: Dice-based time calculation
- **Final Salary**: Adjusted based on experience level

### Dice Integration
- **DiceRollerUI**: Integrated dice rolling for search time
- **Modifiers**: Experience level affects dice results
- **Manual/Auto**: Support for both dice input methods

## JavaScript Functionality

### Initialization
- **`window.onload`**: Loads game data, personnel, tasks, and date
- **URL Parameter**: Extracts `game_id` from query string
- **Error Handling**: Redirects to home if no game ID

### Data Loading Functions
- **`loadPersonnel()`**: Fetches and displays employee data
- **`loadDirectorTasks()`**: Loads director's task queue
- **`loadGameDate()`**: Updates current game date display

### Personnel Display
- **Table Population**: Dynamic row creation for employees
- **Status Indicators**: Color-coded experience and morale badges
- **Empty States**: Handles no personnel scenario

### Task Management
- **`createTaskCard()`**: Generates task display cards
- **Status Badges**: Active/pending state indicators
- **Action Buttons**: Delete functionality for pending tasks

### Hiring Process
- **`showHireModal()`**: Displays position selection interface
- **`startHireSearch()`**: Initiates dice roll and API call
- **Form Validation**: Ensures position and level selection

### Time Advancement
- **Dice Mode Selection**: Auto/manual dice choice
- **Manual Input**: Physical dice value entry
- **Event Processing**: Handles hire resolution events

### Utility Functions
- **`getExpClass/getExpLabel`**: Experience level styling
- **`getMoraleClass/getMoraleLabel`**: Morale level styling
- **Color Coding**: Consistent visual status indicators

## Key Features

### Comprehensive Personnel View
- **Real-time Data**: Live updates from game state
- **Detailed Metrics**: Salary, experience, morale tracking
- **Task Queue**: Visual director workload management

### Interactive Hiring
- **Position Selection**: Dynamic available positions
- **Experience Levels**: Three-tier hiring options
- **Dice Integration**: Proper RPG mechanics
- **Cost Calculation**: Real-time salary adjustments

### Task Management
- **Queue Visualization**: Active and pending tasks
- **Progress Tracking**: Completion date display
- **Queue Management**: Delete pending tasks

### Responsive Design
- **Mobile Adaptive**: Grid layouts for different screens
- **Modal System**: Overlay interfaces for actions
- **Scrollable Content**: Handles large personnel lists

## Dependencies
- **base.html**: Template inheritance and global functions
- **DiceRollerUI**: Integrated dice rolling system
- **API Endpoints**:
  - `/api/games/{id}/personnel` - Employee data
  - `/api/games/{id}/personnel/{id}/tasks` - Director tasks
  - `/api/games/{id}/hire/available-positions` - Position list
  - `/api/games/{id}/hire/start` - Initiate hiring
  - `/api/games/{id}/time/advance` - Time progression

## Integration Points
- **Global Navigation**: Inherited from base.html
- **Toast System**: Uses global notification functions
- **Dice System**: Integrated with universal dice roller
- **Time Management**: Global time advancement system

## User Experience
- **Progressive Disclosure**: Information revealed as needed
- **Visual Feedback**: Color-coded status indicators
- **Error Prevention**: Form validation and confirmation dialogs
- **Efficiency**: Batch operations and quick actions

## Technical Implementation
- **Dynamic DOM**: JavaScript-driven content updates
- **Form Data**: Proper multipart form handling
- **Async Operations**: Modern fetch API usage
- **State Management**: Client-side data caching

## Security Considerations
- **Game ID Validation**: Ensures user owns the game
- **API Authentication**: Proper endpoint security
- **Input Sanitization**: Form data validation
- **Error Boundaries**: Graceful failure handling