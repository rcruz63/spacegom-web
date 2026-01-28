"""
Routes para el sistema de dados.

Este módulo contiene los endpoints relacionados con tiradas de dados,
tanto el endpoint legado HTMX como los nuevos endpoints JSON.
"""
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any

from app.dice import DiceRoller
from app.game_state import GameState

router = APIRouter(tags=["dice"])

templates = Jinja2Templates(directory="app/templates")


@router.post("/api/roll-dice", response_class=HTMLResponse)
async def roll_dice(
    request: Request, 
    num_dices: int = Form(1), 
    manual_result: str | None = Form(None)
) -> HTMLResponse:
    """Tirada de dados (endpoint legado para HTMX).

    Devuelve un fragmento HTML (`components/dice_result.html`) usado por la
    interfaz HTMX. Para clientes programáticos, se recomiendan los
    endpoints JSON.
    """
    is_manual = False
    result_val = 0
    details = ""

    if manual_result and manual_result.strip():
        try:
            result_val = int(manual_result)
            is_manual = True
        except ValueError:
            result_val = 0
            details = "Error: Invalid manual input"
    else:
        rolls = DiceRoller.roll_dice(num_dices)
        result_val = sum(rolls)
        details = f"Rolls: {rolls}"

    return templates.TemplateResponse("components/dice_result.html", {
        "request": request, 
        "result": result_val, 
        "details": details,
        "is_manual": is_manual
    })


@router.post("/api/dice/roll")
async def roll_dice_universal(request: Request) -> Dict[str, Any]:
    """Endpoint universal de tiradas de dados (JSON).

    Espera un JSON con `num_dice`, `dice_sides` y opcionalmente
    `manual_values`. Devuelve los resultados de los dados, la suma y el
    modo (`manual` o `automatic`).
    """
    try:
        data = await request.json()
        num_dice = data.get('num_dice', 1)
        dice_sides = data.get('dice_sides', 6)
        manual_values = data.get('manual_values')
        
        if manual_values:
            # Validate manual values
            if len(manual_values) != num_dice:
                raise HTTPException(400, f"Expected {num_dice} dice values, got {len(manual_values)}")
            for val in manual_values:
                if val < 1 or val > dice_sides:
                    raise HTTPException(400, f"All dice values must be between 1 and {dice_sides}")
            results = manual_values
            mode = "manual"
        else:
            # Automatic roll
            results = DiceRoller.roll_dice(num_dice, dice_sides)
            mode = "automatic"
        
        return {
            "dice": results,
            "sum": sum(results),
            "mode": mode,
            "num_dice": num_dice,
            "dice_sides": dice_sides
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/api/games/{game_id}/roll")
async def roll_dice_json(
    game_id: str,
    num_dice: int = Form(1),
    manual_results: Optional[str] = Form(None),
    purpose: str = Form("")
) -> Dict[str, Any]:
    """Tirar dados y registrar la tirada en el historial del juego.

    Los parámetros coinciden con el formulario de la interfaz. Devuelve
    los resultados, el total, si fue manual y una representación
    formateada. El campo `purpose` se usa para etiquetar la tirada.
    """
    game = GameState(game_id)
    
    is_manual = False
    results = []
    
    if manual_results and manual_results.strip():
        # Parse manual results
        try:
            results = [int(x.strip()) for x in manual_results.split(",")]
            if len(results) != num_dice:
                raise ValueError(f"Expected {num_dice} results, got {len(results)}")
            if any(r < 1 or r > 6 for r in results):
                raise ValueError("All results must be between 1 and 6")
            is_manual = True
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    else:
        # Automatic roll
        results = DiceRoller.roll_dice(num_dice)
    
    # Record in game history
    game.record_dice_roll(num_dice, results, is_manual, purpose)
    
    return {
        "results": results,
        "total": sum(results),
        "is_manual": is_manual,
        "purpose": purpose,
        "formatted": DiceRoller.format_results(results)
    }
