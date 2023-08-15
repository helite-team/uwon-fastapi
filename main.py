from io import BytesIO

from rembg import remove

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}


@app.post("/remove_bg")
async def remove_bg(file: UploadFile):
    try:
        image_data = await file.read()
        output = remove(image_data)
        output_image = BytesIO(output)
        output_image.seek(0)
        return StreamingResponse(output_image, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
