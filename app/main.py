from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import random

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/roll-dice", response_class=HTMLResponse)
async def roll_dice(request: Request, num_dices: int = Form(1), manual_result: str | None = Form(None)):
    is_manual = False
    result_val = 0
    details = ""

    if manual_result and manual_result.strip():
        try:
            result_val = int(manual_result)
            is_manual = True
        except ValueError:
            result_val = 0 # Or handle error
            details = "Error: Invalid manual input"
    else:
        # Roll d6s
        rolls = [random.randint(1, 6) for _ in range(num_dices)]
        result_val = sum(rolls)
        details = f"Rolls: {rolls}"

    return templates.TemplateResponse("components/dice_result.html", {
        "request": request, 
        "result": result_val, 
        "details": details,
        "is_manual": is_manual
    })
