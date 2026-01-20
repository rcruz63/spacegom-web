# setup.html

## Overview
`setup.html` is the game initialization template that guides new players through the complete setup process for starting a SpaceGOM game. It extends `base.html` and provides a step-by-step wizard for establishing company identity, determining game parameters through dice rolls, and selecting starting conditions.

## Structure

### Template Inheritance
- **Extends**: `base.html`
- **Block**: `content` - Contains the setup wizard interface

### Lore Banner
Opening narrative section explaining the inheritance premise:
- **Story**: Player inherits company, ship, and crew from deceased mother
- **Purpose**: Sets context for the setup process

### Setup Form Container
Sequential sections that unlock progressively:

#### Company Identification Section
- **Company Name**: Input field with suggestion button
- **Ship Name**: Input field with suggestion button  
- **Ship Model**: Fixed to "Basic Starfall" (inheritance)
- **Confirm Button**: Saves identity and unlocks next section

#### Area Determination Section
- **Dice Roll**: 2d6 to determine starting area (2-12)
- **Options**: Automatic roll or manual input
- **Result Display**: Shows dice values and assigned area

#### World Density Section
- **Dice Roll**: 2d6 to determine planet density in area
- **Density Levels**: Low (2-4), Medium (5-9), High (10-12)
- **Result Display**: Dice, total, and density classification

#### Ship Position Section
- **Dice Rolls**: 1d6 for column (A-F), 1d6 for row (1-6)
- **Quadrant Display**: Shows resulting coordinate (e.g., B3)
- **Result Display**: Individual die values and final position

#### Starting Planet Section
- **Dice Rolls**: 3d6 for planet code generation (111-666)
- **Planet Validation**: Checks multiple criteria for suitability
- **Data Completion**: Form for missing planet data
- **Validation Checks**: Population, tech level, life support, etc.
- **Retry Option**: Next planet code if current fails validation

#### Difficulty Selection
- **Three Levels**: Easy (600 SC), Normal (500 SC), Hard (400 SC)
- **Capital Impact**: Determines starting funds
- **Progress Display**: Shows setup completion status

#### Completion Section
- **Success Message**: Setup confirmation with initial stats
- **Dashboard Link**: Navigation to main game interface

## JavaScript Functionality

### Initialization
- **`loadInitialNames()`**: Fetches suggested company and ship names on load
- **URL Parameter Handling**: Extracts or creates `game_id`
- **Progressive UI**: Sections unlock sequentially

### Name Suggestion System
- **`suggestCompanyName()`**: API call for random company name
- **`suggestShipName()`**: API call for random ship name
- **Auto-population**: Pre-fills form fields

### Company Setup
- **`saveCompanyDetails()`**: Creates game if needed, saves identity
- **Game Creation**: POST to `/api/games/new` for new games
- **Identity Save**: POST to `/api/games/{id}/company-setup`

### Dice Rolling System
- **Area Roll**: `rollArea(isManual)` - Determines starting area
- **Density Roll**: `rollDensity(isManual)` - Sets world density
- **Position Roll**: `rollPosition(isManual)` - Sets ship coordinates
- **Planet Roll**: `rollPlanet(isManual)` - Generates planet codes

### Manual Input Handling
- **Toggle Functions**: Show/hide manual input fields
- **Validation**: Ensures die values are 1-6
- **Form Data**: Appends manual values to API requests

### Planet Selection System
- **`fetchPlanetData(code)`**: Loads planet information
- **`processPlanetData(data)`**: Updates UI with planet details
- **Validation Display**: Visual checks for each requirement
- **Data Completion**: Form for missing bootstrap data
- **`updatePlanetData()`**: Saves corrected planet information

### Setup Completion
- **`selectStartingPlanet()`**: Sets chosen planet as origin
- **`completeSetupWithDifficulty(difficulty)`**: Finalizes setup
- **Personnel Creation**: Generates initial crew
- **Fund Allocation**: Sets starting capital based on difficulty

## Key Features

### Progressive Disclosure
- **Sequential Steps**: Each section unlocks after previous completion
- **Visual Feedback**: Results displayed with dice animations
- **State Management**: Tracks completion across page reloads

### Validation System
- **Planet Requirements**: Multiple checks for starting world suitability
- **Data Integrity**: Handles missing planet data gracefully
- **Retry Logic**: Next planet option for failed validations

### Dice Integration
- **Multiple Modes**: Automatic rolling or manual input
- **Result Persistence**: Values saved to game state
- **Visual Display**: Dice values shown in result panels

### Error Handling
- **Network Errors**: User-friendly error messages
- **Input Validation**: Prevents invalid die values
- **API Failures**: Graceful degradation with alerts

## Dependencies
- **base.html**: Template inheritance and global functions
- **API Endpoints**:
  - `/api/suggestions/*` - Name generation
  - `/api/games/new` - Game creation
  - `/api/games/{id}/setup` - Setup steps
  - `/api/games/{id}/setup-position` - Position setting
  - `/api/planets/{code}` - Planet data
  - `/api/planets/next/{code}` - Next planet lookup

## Integration Points
- **Game Creation**: Seamless new game initialization
- **State Persistence**: All setup data saved to backend
- **Navigation Flow**: Direct transition to dashboard
- **Data Validation**: Real-time planet suitability checking

## User Experience
- **Guided Process**: Clear step-by-step progression
- **Flexibility**: Manual dice input for physical gaming
- **Feedback**: Immediate results and validation status
- **Recovery**: Handles incomplete or invalid data gracefully

## Technical Implementation
- **Form Data**: Uses FormData for multipart requests
- **Async/Await**: Modern JavaScript for API calls
- **DOM Manipulation**: Dynamic UI updates and transitions
- **State Tracking**: Client-side variables for setup progress