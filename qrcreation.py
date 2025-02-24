from fastapi import FastAPI, Form, Response, Cookie
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import qrcode
import os
from jinja2 import Template
import uuid

app = FastAPI()

# Ensure the "static" directory exists and mount it
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

html_template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>QR Code Generator</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: #f8f9fa;
        }
        .card {
            border: none;
            border-radius: 0.75rem;
        }
        .card-title {
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="card shadow-sm">
                    <div class="card-body">
                        <h2 class="card-title text-center mb-4">Generate a QR Code</h2>
                        <form action="/generate_qr" method="post">
                            <div class="mb-3">
                                <label for="text" class="form-label">Enter text:</label>
                                <input type="text" id="text" name="text" class="form-control" placeholder="Your text here" required>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">Generate QR Code</button>
                            </div>
                        </form>
                        {% if qr_path %}
                        <hr>
                        <div class="text-center">
                            <h3 class="mt-4">Your QR Code:</h3>
                            <img src="{{ qr_path }}" alt="QR Code" class="img-fluid my-3" style="max-width: 300px;">
                            <a href="/download_qr" download class="btn btn-success">Download QR Code</a>
                        </div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
""")

@app.get("/", response_class=HTMLResponse)
async def home():
    # Display homepage without QR code
    return html_template.render(qr_path=None)

@app.post("/generate_qr", response_class=HTMLResponse)
async def generate_qr(text: str = Form(...)):
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")

    unique_filename = f"qr_code_{uuid.uuid4().hex}.png"
    file_path = os.path.join("static", unique_filename)
    img.save(file_path)

    # Render the template and set a cookie with the unique filename
    html_content = html_template.render(qr_path=f"/static/{unique_filename}")
    response = HTMLResponse(content=html_content)
    response.set_cookie(key="qr_code", value=unique_filename)
    return response

@app.get("/download_qr")
async def download_qr(qr_code: str = Cookie(None)):
    if not qr_code:
        return HTMLResponse("No QR code found in your session.", status_code=400)
    file_path = os.path.join("static", qr_code)
    return FileResponse(file_path, media_type="image/png", filename=qr_code)
