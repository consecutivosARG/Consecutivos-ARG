from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import openpyxl
import os
from datetime import datetime

app = FastAPI()

# Configuración de archivos estáticos y plantillas
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ruta del archivo Excel
RUTA_EXCEL = r"C:\Users\cordi\OneDrive - ARG Consultores y servicios S.A.S\02. PERSONAL\consecutivos\01. Correspondencia contratos en ejecución (1).xlsx"

# Credenciales de usuario (Esto debería mejorarse con autenticación segura)
USERS = {
    "admin": "1234",
    "usuario1": "clave1"
}

# Variable para almacenar la sesión del usuario
user_sessions = {}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in USERS and USERS[username] == password:
        user_sessions["logged_in_user"] = username
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request, "error": "❌ Credenciales incorrectas"}, status_code=401)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if "logged_in_user" not in user_sessions:
        return RedirectResponse(url="/", status_code=303)
    
    if os.path.exists(RUTA_EXCEL):
        xl = pd.ExcelFile(RUTA_EXCEL)
        hojas = xl.sheet_names
    else:
        hojas = []

    return templates.TemplateResponse("dashboard.html", {"request": request, "hojas": hojas, "username": user_sessions["logged_in_user"]})

@app.post("/insert_project/")
async def insert_project(sheet_name: str = Form(...), asunto: str = Form(...), elaborado_por: str = Form(...)):
    if "logged_in_user" not in user_sessions:
        return JSONResponse(content={"error": "No autenticado"}, status_code=401)

    try:
        wb = openpyxl.load_workbook(RUTA_EXCEL)
        hoja = wb[sheet_name]

        # Buscar la primera fila vacía en la columna "Asunto" (Columna D)
        primera_fila_vacia = None
        for fila in range(2, hoja.max_row + 1):
            if hoja[f'D{fila}'].value is None:
                primera_fila_vacia = fila
                break

        if primera_fila_vacia is None:
            return JSONResponse(content={"error": "No hay espacio disponible en la hoja."}, status_code=400)

        # Obtener el último consecutivo y generar el nuevo
        ultimo_consecutivo = hoja[f'B{primera_fila_vacia - 1}'].value
        if ultimo_consecutivo is None:
            nuevo_consecutivo = "C069001"  # Si es la primera vez, asignar el inicial
        else:
            num = int(ultimo_consecutivo[5:]) + 1  # Extraer los números y sumarle 1
            nuevo_consecutivo = f"C069{num:03d}"  # Mantener formato C069XXX

        # Guardar la información
        hoja[f'B{primera_fila_vacia}'] = nuevo_consecutivo  # Consecutivo
        hoja[f'C{primera_fila_vacia}'] = datetime.now().strftime('%d/%m/%Y')  # Fecha actual
        hoja[f'D{primera_fila_vacia}'] = asunto
        hoja[f'E{primera_fila_vacia}'] = elaborado_por

        wb.save(RUTA_EXCEL)
        wb.close()

        return JSONResponse(content={"message": f"✅ Proyecto agregado en la fila {primera_fila_vacia} con consecutivo {nuevo_consecutivo}", "consecutivo": nuevo_consecutivo})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/logout")
async def logout():
    user_sessions.pop("logged_in_user", None)
    return RedirectResponse(url="/", status_code=303)

