from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class GpsCoords(BaseModel):
    lat: str
    log: str


app = FastAPI()


def verify_token(req: Request):
        token = req.headers["Authorization"]
        # Here your code for verifying the token or whatever you use
        if token is not "a510e951d4b9b39d0167b26cc42ddf6a":
            raise HTTPException(
                status_code=401,
                detail="Unauthorized"
            )
        return True


@app.post("/coords/")
async def log_gps_cords(coords: GpsCoords, authorized: bool = Depends(verify_token)):
    if authorized:
        logger.info(coords)
        return coords
    
    