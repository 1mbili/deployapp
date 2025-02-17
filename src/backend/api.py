from fastapi import Request, status, APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.backend.azure_blob_handler import AzureBlobHandler
from src.backend.azure_cosmosdb_handler import AzureCosmosDBHandler
from typing import List, Optional

import uuid

templates = Jinja2Templates(directory="src/templates")


router = APIRouter(
    prefix="/image",
    tags=["image"],
    responses={404: {"description": "Not found"}},
)

@router.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )

@router.get("/upload", response_class=HTMLResponse)
async def upload_image(request: Request):
    return templates.TemplateResponse(
        request=request, name="upload.html"
    )


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def post_recipt_image(request: Request, 
                            file: UploadFile = File(...),
                            tag_key: Optional[List[str]] = Form(None),
                            tag_value: Optional[List[str]] = Form(None)):
    if file.content_type not in ["application/pdf", "image/png", "image/jpg", "image/jpeg"]:
        raise HTTPException(400, detail="Invalid file type")
    content = await file.read()
    if "x-ms-client-principal-name" in request.headers:
        container_prefix = f"prod/{request.headers['x-ms-client-principal-name']}"
        user_id = request.headers['x-ms-client-principal-id']
    else: 
        container_prefix = "dev"
        user_id = "dev"
    az_handler = AzureBlobHandler(prefix=container_prefix)
    print("Uploading file")
    az_handler.upload_blob(file.filename, content)
    print("File Uploaded succesfully") 
    cosmos_handler = AzureCosmosDBHandler()
    tags = {"id": uuid.uuid4().hex, "userId": user_id, "fileName": file.filename}
    print(tag_key, tag_value)
    if tag_key and tag_value:
        user_tags = {key: value for key, value in zip(tag_key, tag_value) if key and value}
        tags.update(user_tags)
    cosmos_handler.upload_document(tags)
    return "OK"
