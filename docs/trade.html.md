# trade.html

## Overview
`trade.html` is the trade terminal interface for the SpaceGOM Companion application. It extends `base.html` and provides a complete marketplace for buying and selling goods with dice-based negotiation mechanics.

## Structure

### Template Inheritance
- **Extends**: `base.html`
- **Block**: `content` - Contains the trade terminal interface

### Header Section
- **Title**: "TERMINAL DE COMERCIO" with scales emoji
- **Subtitle**: "Mercado Galáctico // Convenio Spacegom"
- **Status Cards**: Credits, Storage, Current Planet

### Main Content Grid

#### Buy Section (Oferta)
- **Title**: "OFERTA (COMPRAR)" with green styling
- **Dynamic List**: Available products for purchase
- **Product Cards**: Detailed information and negotiate buttons

#### Sell Section (Demanda)
- **Title**: "DEMANDA (VENDER)" with red styling
- **Dynamic List**: Current cargo available for sale
- **Order Cards**: Existing trade orders with sell buttons

### Trade Ledger
- **Title**: "REGISTRO DE PEDIDOS (LEDGER)"
- **Refresh Button**: Manual data reload
- **Table**: Comprehensive trade history
- **Columns**: ID, Product, UCN, Buy/Sell details, Profit, Status

## Negotiation Modal System

### Step 1: Dice Input
- **Auto Roll**: Automatic 2d6 dice generation
- **Manual Input**: Physical dice value entry
- **Visual Feedback**: Clear action buttons

### Step 2: Results & Confirmation
- **Roll Display**: Dice results and total
- **Outcome**: Success/Failure/Normal with color coding
- **Modifiers**: Reputation and skill bonuses
- **Price Calculation**: Before/after pricing with totals
- **Quantity Input**: Dynamic for buy orders
- **Action Buttons**: Accept/Reject trade

## JavaScript Functionality

### Data Loading
- **`loadTradeData()`**: Comprehensive data fetch function
- **Game State**: Treasury, storage, current planet
- **Market Data**: Buy/sell items from current planet
- **Trade Ledger**: Historical order information

### Market Rendering
- **`renderMarket(data)`**: Populates buy/sell sections
- **Buy Items**: Product details, pricing, production cycles
- **Sell Items**: Existing cargo with sell options
- **Empty States**: Handles no available trades

### Ledger Display
- **`renderLedger(orders)`**: Populates trade history table
- **Sorting**: Orders by ID descending
- **Status Badges**: Sold/In Transit indicators
- **Profit Display**: Color-coded financial results

### Negotiation System
- **`openNegotiation(actionType, itemId)`**: Initializes trade modal
- **`startNegotiation(mode)`**: Processes dice rolls and modifiers
- **Result Calculation**: Multipliers based on roll outcomes
- **Price Updates**: Dynamic pricing with quantity changes

### Trade Execution
- **`confirmTrade()`**: Finalizes buy/sell transactions
- **Form Data**: Proper API payload construction
- **Planet Context**: Extracts current planet from UI
- **Error Handling**: Comprehensive validation and feedback

## Key Features

### Comprehensive Marketplace
- **Real-time Data**: Live market information from current planet
- **Detailed Product Info**: Production cycles, demand patterns, margins
- **Storage Limits**: Respects planetary UCN restrictions
- **Profit Tracking**: Historical trade performance

### Dice-Based Negotiation
- **RPG Mechanics**: 2d6 rolls with modifiers
- **Multiple Modes**: Auto/manual dice input
- **Dynamic Pricing**: Success/failure affects final prices
- **Modifier System**: Reputation and skill bonuses

### Trade Ledger
- **Complete History**: All buy/sell transactions
- **Status Tracking**: Order lifecycle management
- **Financial Analysis**: Profit/loss calculations
- **Data Export**: Structured tabular display

### Interactive Modal
- **Progressive Steps**: Dice input → Results → Confirmation
- **Visual Feedback**: Color-coded outcomes and pricing
- **Quantity Selection**: Dynamic total calculations
- **Error Prevention**: Input validation and confirmation

## Dependencies
- **base.html**: Template inheritance and global functions
- **API Endpoints**:
  - `/api/games/{id}/trade/market` - Market data
  - `/api/games/{id}/trade/orders` - Trade history
  - `/api/games/{id}/trade/negotiate` - Price negotiation
  - `/api/games/{id}/trade/buy` - Purchase execution
  - `/api/games/{id}/trade/sell` - Sale execution

## Integration Points
- **Global Navigation**: Inherited from base.html
- **Toast System**: Uses global notification functions
- **Game State**: Real-time treasury and storage updates
- **Planet Context**: Current location affects available trades

## User Experience
- **Market Overview**: Clear buy/sell sections
- **Negotiation Flow**: Intuitive dice-based pricing
- **Financial Tracking**: Comprehensive trade history
- **Mobile Responsive**: Adaptive grid layouts

## Technical Implementation
- **Dynamic DOM**: JavaScript-driven content updates
- **Form Data**: Multipart form handling for API calls
- **Async Operations**: Modern fetch API with error handling
- **State Management**: Client-side market data caching

## Game Mechanics
- **Negotiation Rolls**: 2d6 + modifiers determine price multipliers
- **Success Thresholds**: Roll-based success/failure outcomes
- **Price Multipliers**: Affect final transaction costs
- **Quantity Limits**: Planetary UCN restrictions
- **Profit Calculation**: Automatic margin tracking

## Security Considerations
- **Game ID Validation**: Ensures user owns the game
- **API Authentication**: Proper endpoint security
- **Input Sanitization**: Form data validation
- **Client Trust**: Price calculations validated server-side