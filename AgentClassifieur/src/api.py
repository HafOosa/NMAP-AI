from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from router import predict_complexity
import uvicorn
import traceback

app = FastAPI(title="NMAP-AI Complexity Router", version="1.0")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    predicted_complexity: str
    confidence: float
    all_probabilities: dict
    explanation: str = None

@app.get("/")
def home():
    return {"message": "NMAP-AI Router prêt ! POST /predict avec {'query': 'votre phrase'}"}

@app.post("/predict", response_model=QueryResponse)
def predict(request: QueryRequest):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Requête vide")
        
        result = predict_complexity(request.query)
        
        if result["predicted_complexity"] in ["IRRELEVANT", "EMPTY"]:
            raise HTTPException(status_code=400, detail=result.get("explanation", "Requête invalide"))
        
        return result
    
    except Exception as e:
        # On capture TOUTE erreur et on la renvoie clairement
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        print("\nERREUR DANS L'API :\n", traceback_str)  # affiché dans le terminal serveur
        raise HTTPException(status_code=500, detail=f"Erreur interne : {error_detail}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)