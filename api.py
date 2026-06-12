from fastapi import FastAPI, UploadFile, File
import uvicorn
from database import check_compliance
from alpr_engine import AFACSEngine
import database

app = FastAPI(title="AFACS NextGen ALPR API")
engine = AFACSEngine()

@app.on_event("startup")
def startup_event():
    database.init_db()

@app.post("/verify_vehicle")
async def verify_vehicle(file: UploadFile = File(...)):
    # Read the image file
    contents = await file.read()
    
    # Process through ALPR Engine
    out_img, plates_found = engine.process_image(contents)
    
    if not plates_found:
        return {"error": "No vehicles or license plates detected."}
    
    # Take the most confident plate
    best_plate = plates_found[0]['text']
    confidence = plates_found[0]['confidence']
    
    # Check compliance in ledger
    compliance_info = check_compliance(best_plate)
    
    return {
        "plate_detected": best_plate,
        "confidence": confidence,
        "compliance": compliance_info
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
