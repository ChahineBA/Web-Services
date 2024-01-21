from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
import requests
from typing import List, Dict, Any
from pydantic import BaseModel,Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
ouath_scheme = OAuth2PasswordBearer(tokenUrl="token")
router = APIRouter()

# TOKEN 
@router.post("/token", summary="Generate Access Token", tags=["Authentication"])
async def token_generate(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response_model=dict,
    response_description="Access Token generated successfully",
):
    """
    Endpoint to generate an access token.

    - **form_data**: OAuth2PasswordRequestForm
      - `username`: The username.
      - `password`: The password.

    - **Returns**: dict
      - `access_token`: The generated access token.
      - `token_type`: The token type (e.g., "bearer").
    """
    return {"access_token": form_data.username, "token_type": "bearer"}


# Dummy data for estimations
estimations = []

class EstimationData(BaseModel):
    year: str = Field(..., description="The year of the estimation.")
    month: str = Field(..., description="The month of the estimation.")
    day: str = Field(..., description="The day of the estimation.")
    cycle: str = Field(..., description="The cycle value for the estimation.")
    trend: str = Field(..., description="The trend value for the estimation.")
class DeleteEstimationData(BaseModel):
    year: str = Field(..., description="The year of the estimation.")
    month: str = Field(..., description="The month of the estimation.")
    day: str = Field(..., description="The day of the estimation.")
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},          
    )

# GET ESTIMATIONS
@router.get("/get_estimations", summary="Get Atmospheric CO2 Estimations", tags=["Estimations"])
async def get_estimations(
    request: Request,
    token: str = Depends(ouath_scheme),
    response_model=List[Dict[str, float]],
    response_description="List of Atmospheric CO2 Estimations",
):
    """
    Endpoint to get atmospheric CO2 estimations.

    - **token**: str
      - The access token obtained through authentication.

    - **Returns**: List[Dict[str, float]]
      - A list of dictionaries representing atmospheric CO2 estimations.
        Each dictionary contains CO2 values for a specific day.
    """
    global estimations
    url = "https://daily-atmosphere-carbon-dioxide-concentration.p.rapidapi.com/api/co2-api"

    headers = {
        "X-RapidAPI-Key": "0597d15aebmsh830e40a2a6e4346p191508jsn0bcf1770c3c2",
        "X-RapidAPI-Host": "daily-atmosphere-carbon-dioxide-concentration.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    results = response.json()
    estimations = results['co2']

    return response.json()

# GET ESTIMATIONS
@router.get("/estimations", summary="Get Atmospheric CO2 Estimations", tags=["Estimations"])
async def read_estimations(
    token: str = Depends(ouath_scheme),
    response_model=List[Dict[str, Any]],
    response_description="List of Atmospheric CO2 Estimations",
):
    """
    Endpoint to get atmospheric CO2 estimations.

    - **token**: str
      - The access token obtained through authentication.

    - **Returns**: List[Dict[str, Any]]
      - A list of dictionaries representing atmospheric CO2 estimations.
        Each dictionary contains CO2 values for a specific day.

    - **Response Model**:
      - List[Dict[str, Any]]
        - A list of dictionaries where each dictionary contains CO2 values for a specific day.

    - **Response Description**: "List of Atmospheric CO2 Estimations"
      - A description of the response content, providing context for the returned data.
    """
    try:
        global estimations
        # Validate the data against the Recipe model before returning
        return estimations
    except Exception as error:
        print(f"Error in /estimations endpoint: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# CREATE ESTIMATIONS
@router.post("/estimations", summary="Create New Atmospheric CO2 Estimation", tags=["Estimations"])
async def create_estimation(
    request: Request,
    token: str = Depends(ouath_scheme),
    estimation_data: EstimationData = Depends(),
    response_model=List[Dict[str, Any]],
    response_description="List of Atmospheric CO2 Estimations",
):
    """
    Endpoint to create a new atmospheric CO2 estimation.

    - **token**: str
      - The access token obtained through authentication.

    - **request_body**: Dict[str, Any]
      - The request body containing the data for the new atmospheric CO2 estimation.

    - **Returns**: List[Dict[str, Any]]
      - A list of dictionaries representing atmospheric CO2 estimations.
        Each dictionary contains CO2 values for a specific day.

    - **Response Model**:
      - List[Dict[str, Any]]
        - A list of dictionaries where each dictionary contains CO2 values for a specific day.

    - **Response Description**: "List of Atmospheric CO2 Estimations"
      - A description of the response content, providing context for the returned data.
    """
    try:
        global estimations
        estimations.append(estimation_data.dict())
        return estimations
    except Exception as error:
        print(f"Error in /estimations endpoint: {error}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Update Estimations
@router.put("/estimations", summary="Update Atmospheric CO2 Estimation", tags=["Estimations"])
async def update_estimation(
    request: Request,
    token: str = Depends(ouath_scheme),
    estimation_data: EstimationData = Depends(),
    response_model=Dict[str, Any],
    response_description="Updated Atmospheric CO2 Estimation",
):
    """
    Endpoint to update an existing atmospheric CO2 estimation.

    - **token**: str
      - The access token obtained through authentication.

    - **request_body**: Dict[str, Any]
      - The request body containing the updated data for the atmospheric CO2 estimation.

    - **Returns**: Dict[str, Any]
      - A dictionary representing the updated atmospheric CO2 estimation.

    - **Response Model**:
      - Dict[str, Any]
        - A dictionary containing CO2 values for a specific day.

    - **Response Description**: "Updated Atmospheric CO2 Estimation"
      - A description of the response content, indicating that it represents the updated estimation.
    """
    try:
        global estimations
        estimation_index = next(
            (
                index
                for index, r in enumerate(estimations)
                if r["year"] == estimation_data.year
                and r["month"] == estimation_data.month
                and r["day"] == estimation_data.day
            ),
            None,
        )
        if estimation_index is not None:
            # Update the estimation data
            estimations[estimation_index].update(estimation_data.dict(exclude_unset=True))
            return estimations[estimation_index]
        else:
            raise HTTPException(status_code=404, detail="Estimation not found")
    except Exception as error:
        print(f"Error in /estimations endpoint: {error}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(error)}")

# DELETE ESTIMATION
@router.delete("/estimations", summary="Delete Atmospheric CO2 Estimation", tags=["Estimations"])
async def delete_estimation(
    request: Request,
    token: str = Depends(ouath_scheme),
    estimation_data: DeleteEstimationData = Depends(),
    response_model=Dict[str, Any],
    response_description="Deleted Atmospheric CO2 Estimation",
):
    """
    Endpoint to delete an existing atmospheric CO2 estimation.

    - **token**: str
      - The access token obtained through authentication.

    - **request_body**: Dict[str, Any]
      - The request body containing the data of the atmospheric CO2 estimation to be deleted.

    - **Returns**: Dict[str, Any]
      - A dictionary representing the deleted atmospheric CO2 estimation.

    - **Response Model**:
      - Dict[str, Any]
        - A dictionary containing CO2 values for a specific day.

    - **Response Description**: "Deleted Atmospheric CO2 Estimation"
      - A description of the response content, indicating that it represents the deleted estimation.
    """
    try:
        global estimations
        print("Before Deletion:", estimations)  # Add this line for debugging

        # Ensure that attributes are not None before using them
        if None in (estimation_data.year, estimation_data.month, estimation_data.day):
            raise HTTPException(status_code=422, detail="Invalid input data")

        estimation = next(
            (r for r in estimations if r["year"] == estimation_data.year
             and r["month"] == estimation_data.month
             and r["day"] == estimation_data.day),
            None,
        )
        if estimation:
            # Use a different variable name locally
            estimation_list = [
                r
                for r in estimations
                if not (
                    r["year"] == estimation_data.year
                    and r["month"] == estimation_data.month
                    and r["day"] == estimation_data.day
                )
            ]
            estimations[:] = estimation_list  # Update the global variable
            print("After Deletion:", estimations)  # Add this line for debugging
            return estimations
        else:
            raise HTTPException(status_code=404, detail="Estimation not found")
    except HTTPException as http_error:
        print(f"HTTP Exception: {http_error}")
        raise
    except Exception as error:
        print(f"Error in /estimations endpoint: {error}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(error)}")

