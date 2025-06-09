import json
import traceback
from typing import List
from uuid import UUID
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from Alc_Detection.Application.Requests.Models import CalibrationBoxesResponse
from Alc_Detection.Application.VideoAnalytics.ShelfService import ShelfService
from Alc_Detection.Application.Requests.Requests import AddCalibrationBoxesRequest
from Alc_Detection.Application.Requests.Models import CalibrationBox as CalibrationBoxModel

class ShelfController:
    def __init__(self, 
                 shelfService: ShelfService):
        self.shelfService = shelfService
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route("/realograms/", self.handle_shelf_image, methods=["POST"], status_code=status.HTTP_200_OK)
        self.router.add_api_route("/calibrations/", self.calibrate_planogram, methods=["POST"], status_code=status.HTTP_200_OK)
        self.router.add_api_route("/calibration_boxes/", self.get_calibration_boxes, methods=["POST"], status_code=status.HTTP_200_OK)
        self.router.add_api_route("/product_images/{product_id}", self.add_product_images, methods=["POST"], status_code=status.HTTP_200_OK)
        self.router.add_api_route("/images/{store_id}/{shelving_id}", self.get_test_image, methods=["POST"], status_code=status.HTTP_200_OK)
        
    async def get_test_image(
        self,
        image_file: UploadFile = File(...),
    ) -> dict:
        try:      
            return {"message": "Cool"}        
        except HTTPException as he:
            raise he        
        except Exception as e:
            traceback.print_exc() 
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    async def add_product_images(
        self,
        product_id: UUID,
        image_files: List[UploadFile] = File(...)
    ) -> dict:
        try:      
            message = await self.shelfService.add_product_images(
                product_id=product_id,
                image_files=image_files
            )         
            return {"message": message}        
        except HTTPException as he:
            raise he        
        except Exception as e:
            traceback.print_exc() 
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )       
    
    async def handle_shelf_image(
        self,
        image_file: UploadFile = File(...),
        shelving_id: UUID = Form(...),
        store_id: UUID = Form(...)
    ) -> dict:
        try:      
            message = await self.shelfService.handle_shelf_image(
                image_file=image_file,
                shelving_id=shelving_id,
                store_id=store_id
            )           
            return {"message": message}        
        except HTTPException as he:
            raise he        
        except Exception as e:
            traceback.print_exc() 
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    async def get_calibration_boxes(self,
                                    image_file: UploadFile = File(...)
    ) -> CalibrationBoxesResponse:
        try:      
            response = await self.shelfService.get_calibration_boxes(image_file=image_file)           
            return response        
        except HTTPException as he:
            raise he        
        except Exception as e:
            traceback.print_exc() 
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )    
    
    async def calibrate_planogram(
        self,
        order_id: UUID = Form(...),
        person_id: UUID = Form(...),
        shelving_id: UUID = Form(...),
        store_id: UUID = Form(...),
        calibration_boxes: str = Form(...), 
        image_file: UploadFile = File(...)
    ) -> dict:
        try:      
            boxes = json.loads(calibration_boxes)
            message = await self.shelfService.calibrate_planogram(
                order_id = order_id,
                person_id = person_id,
                shelving_id = shelving_id,
                store_id = store_id,
                calibration_boxes = boxes,
                image_file = image_file,
            )
            return {"message": message}        
        except HTTPException as he:
            raise he        
        except Exception as e:
            traceback.print_exc() 
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )