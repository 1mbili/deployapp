from fastapi import Depends, status, APIRouter, UploadFile, File, HTTPException

router = APIRouter(
    prefix="/image",
    tags=["image"],
    responses={404: {"description": "Not found"}},
)

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def post_recipt_image(file: UploadFile = File()):
    if file.content_type not in ["application/pdf", "image/png", "image/jpg", "image/jpeg"]:
        raise HTTPException(400, detail="Invalid file type")
    content = await file.read()
    return "OK"
