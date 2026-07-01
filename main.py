import os
import io
import uuid
import base64
import json
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Form, File, UploadFile, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pydantic import BaseModel
from pypdf import PdfReader

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5, AES
from Crypto.Util.Padding import unpad

from gemini_client import generate_resume_json
from resume_generator import generate_resume_pdf
from email_sender import send_resume_email

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("thirdeye_backend")

load_dotenv()

app = FastAPI(title="Thirdeye Resume Generator")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

OUTPUT_DIR = Path("generated")
OUTPUT_DIR.mkdir(exist_ok=True)

class ConfirmPayload(BaseModel):
    resume_data: dict
    company_name: str
    email_to: Optional[str] = None

logger.info("Initializing server and generating new 2048-bit RSA key pair...")
rsa_key = RSA.generate(2048)
rsa_private_cipher = PKCS1_v1_5.new(rsa_key)
public_key_pem = rsa_key.publickey().export_key().decode('utf-8')
logger.info("RSA key pair generated successfully.")

def decrypt_payload(encrypted_aes_key_b64: str, encrypted_iv_b64: str, encrypted_data_b64: str) -> dict:
    logger.debug("Attempting to decrypt incoming hybrid payload...")
    try:
        enc_aes_key = base64.b64decode(encrypted_aes_key_b64)
        enc_iv = base64.b64decode(encrypted_iv_b64)
        
        sentinel = b'error'
        
        aes_key_b64 = rsa_private_cipher.decrypt(enc_aes_key, sentinel)
        iv_b64 = rsa_private_cipher.decrypt(enc_iv, sentinel)
        
        if aes_key_b64 == sentinel or iv_b64 == sentinel:
            raise ValueError("RSA Decryption step failed. Possible key mismatch or corruption.")

        raw_aes_key = base64.b64decode(aes_key_b64)
        raw_iv = base64.b64decode(iv_b64)

        cipher_aes = AES.new(raw_aes_key, AES.MODE_CBC, raw_iv)
        encrypted_data = base64.b64decode(encrypted_data_b64)
        decrypted_bytes = unpad(cipher_aes.decrypt(encrypted_data), AES.block_size)
        
        logger.debug("Payload decrypted successfully.")
        return json.loads(decrypted_bytes.decode('utf-8'))
    except Exception as e:
        logger.error(f"Decryption Error occurred: {type(e).__name__} - {str(e)}")
        return None

@app.get("/", response_class=HTMLResponse)
def form(request: Request):
    logger.info("Served frontend index.html")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/public-key")
def get_public_key():
    logger.info("Frontend requested RSA public key.")
    return {"public_key": public_key_pem}

@app.post("/api/draft")
async def draft_resume(
    encrypted_key: str = Form(...),
    encrypted_iv: str = Form(...),
    encrypted_payload: str = Form(...),
    resume_pdf: Optional[UploadFile] = File(None)
):
    logger.info("Received /api/draft request. Starting payload decryption.")
    
    decrypted_data = decrypt_payload(encrypted_key, encrypted_iv, encrypted_payload)
    if not decrypted_data:
        logger.warning("Draft request rejected: Failed to decrypt payload.")
        return JSONResponse(status_code=400, content={"error": "Failed to decrypt payload. Keys may have mismatched."})

    gemini_key = decrypted_data.get("gemini_key", "")
    gemini_model = decrypted_data.get("gemini_model", "")
    job_description = decrypted_data.get("job_description", "")
    company_name = decrypted_data.get("company_name", "")
    years_exp = decrypted_data.get("years_exp", "")
    resume_text = decrypted_data.get("resume_text", "")

    logger.info(f"Payload extracted. Model: {gemini_model}, Key provided: {'Yes' if gemini_key else 'No'}")

    extracted_resume_text = ""
    
    if resume_pdf and resume_pdf.filename:
        logger.info(f"Processing uploaded PDF. Filename provided: {'Yes' if resume_pdf.filename else 'No'}")
        if not resume_pdf.filename.lower().endswith('.pdf'):
            logger.warning("Uploaded file is not a PDF.")
            return JSONResponse(status_code=400, content={"error": "File must be a PDF."})
            
        content = await resume_pdf.read()
        try:
            pdf_reader = PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    extracted_resume_text += text + "\n"
            logger.info(f"Successfully extracted text from PDF. Pages processed: {len(pdf_reader.pages)}")
        except Exception as e:
            logger.error(f"Failed to read PDF file: {type(e).__name__}")
            return JSONResponse(status_code=400, content={"error": f"Failed to read PDF: {str(e)}"})
            
    elif resume_text and resume_text.strip():
        logger.info("Processing pasted raw text instead of PDF.")
        extracted_resume_text = resume_text.strip()
    else:
        logger.warning("No resume data (PDF or text) provided in request.")
        return JSONResponse(status_code=400, content={"error": "Please provide your resume either as text or as a PDF upload."})

    logger.info("Sending extracted data to Gemini model for structuring...")
    try:
        data = generate_resume_json(
            gemini_key=gemini_key, 
            gemini_model=gemini_model, 
            resume_text=extracted_resume_text, 
            job_description=job_description, 
            company_name=company_name, 
            years_exp=years_exp
        )
        logger.info("Successfully received structured draft from Gemini.")
        return JSONResponse(content={"draft": data})
    except Exception as e:
        logger.error(f"Error during Gemini generation: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

class EncryptedPayload(BaseModel):
    encrypted_key: str
    encrypted_iv: str
    encrypted_payload: str

@app.post("/api/confirm")
def confirm_resume(payload: EncryptedPayload, background_tasks: BackgroundTasks):
    logger.info("Received /api/confirm request. Starting payload decryption.")
    
    decrypted_data = decrypt_payload(
        payload.encrypted_key, 
        payload.encrypted_iv, 
        payload.encrypted_payload
    )
    
    if not decrypted_data:
        logger.warning("Confirm request rejected: Failed to decrypt confirmation payload.")
        return JSONResponse(
            status_code=400, 
            content={"error": "Failed to decrypt confirmation payload."}
        )

    data = decrypted_data.get("resume_data")
    company_name = decrypted_data.get("company_name", "Unknown_Company")
    
    safe_company_name_len = len(company_name)
    logger.info(f"Payload decrypted. Generating PDF for target company (Name length: {safe_company_name_len}).")

    req_uuid = uuid.uuid4().hex[:6]
    filename = f"resume_{company_name.replace(' ', '_')}_{req_uuid}.pdf"
    output_path = str(OUTPUT_DIR / filename)
    
    try:
        logger.info(f"Compiling PDF document with UUID: {req_uuid}")
        generate_resume_pdf(data, output_path)
        logger.info(f"PDF generated successfully at {output_path}. Sending FileResponse.")

        background_tasks.add_task(cleanup_file, output_path)
        
        return FileResponse(output_path, media_type="application/pdf", filename=filename)
    except Exception as e:
        logger.error(f"Error compiling PDF: {str(e)}")
        return JSONResponse(status_code=500, content={"error": "Server error during PDF compilation."})
    


def cleanup_file(path: str):
    if os.path.exists(path):
        try:
            os.remove(path)
            logger.info(f"Successfully cleaned up file: {path}")
        except Exception as e:
            logger.error(f"Failed to delete file {path}: {str(e)}")