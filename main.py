from io import BytesIO

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
from rembg import remove

app = FastAPI()


@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}


def print_ram_usage():
    import psutil

    virtual_memory = psutil.virtual_memory()

    print(f"Total Memory: {virtual_memory.total / (1024**3):.2f} GB")
    print(f"Available Memory: {virtual_memory.available / (1024**3):.2f} GB")
    print(f"Used Memory: {virtual_memory.used / (1024**3):.2f} GB")
    print(f"Memory Percentage Used: {virtual_memory.percent} %")


def resize_image(image_data: bytes, max_size=400):
    with Image.open(BytesIO(image_data)) as img:
        # Calculate new dimensions while preserving aspect ratio
        width, height = img.size
        if width > height:
            new_width = min(max_size, width)
            new_height = int(height * (new_width / width))
        else:
            new_height = min(max_size, height)
            new_width = int(width * (new_height / height))

        # Resize the image
        img.thumbnail((new_width, new_height))

        output_image_io = BytesIO()
        img.save(output_image_io, format="PNG")
        return output_image_io.getvalue()


@app.post("/remove_bg")
async def remove_bg(file: UploadFile):
    try:
        image_data = await file.read()
        resized_image = resize_image(image_data, max_size=400)
        output = remove(resized_image)
        output_image = BytesIO(output)
        output_image.seek(0)

        def generate():
            try:
                yield output_image.read()
            finally:
                output_image.close()

        return StreamingResponse(content=generate(), media_type="image/png")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
