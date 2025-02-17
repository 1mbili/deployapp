from fastapi import Request, status, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.backend.azure_blob_handler import AzureBlobHandler

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
async def post_recipt_image(request: Request, file: UploadFile = File(...)):
    if file.content_type not in ["application/pdf", "image/png", "image/jpg", "image/jpeg"]:
        raise HTTPException(400, detail="Invalid file type")
    content = await file.read()
    container_prefix = f"prod/{request.headers['x-ms-client-principal-name']}"
    az_handler = AzureBlobHandler(prefix=container_prefix)
    print("Uploading file")
    az_handler.upload_blob(file.filename, content)
    return "OK"
