from fastapi import FastAPI, HTTPException, Form
from typing import Annotated
from translatepy import Translator
from translatepy.translators import GoogleTranslateV2, DeeplTranslate
from translatepy.exceptions import TranslatepyException, UnknownLanguage, NoResult
import urllib3
import regex
import logging

logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logging.info(f'[POST] [translate] ===== Starting service =====')

urllib3.disable_warnings()
app = FastAPI()
google = GoogleTranslateV2()
deepl = DeeplTranslate()

@app.get("/check")
def checkResponse():
    return {'status': 'Ok'}

@app.post("/translate/")
def handleTranslation(html: Annotated[str, Form()], target_language: Annotated[str, Form()], service: Annotated[str, Form()]):
    logging.info(f'[POST] [translate] --- Processing request.')
    valid_service = True
    response = []

    try:
        logging.info(f'[POST] [translate] Running translation with {service}.')
        if service == "google":
            result = google.translate_html(html, destination_language=target_language, source_language="auto")
        elif service == "deepl":
            result = deepl.translate_html(html, destination_language=target_language, source_language="auto")
        else:
            valid_service = False

    except NoResult as err:
        logging.error(f'[POST] [translate] Failed to process request. {err}')
        raise HTTPException(status_code=500, detail=f"No result for query was retrieved. Params: {html}, {target_language}, {service}. Stack trace: {err}")
    except UnknownLanguage as err:
        logging.error(f'[POST] [translate] Failed to process request. {err}')
        raise HTTPException(status_code=400, detail=f"An error occured while searching for the language you passed in. Similarity: {round(err.similarity)}. Stack trace: {err}")
    except TranslatepyException as err:
        logging.error(f'[POST] [translate] Failed to process request. {err}')
        raise HTTPException(status_code=500, detail=f"An error occured while translating with translatepy. Stack trace: {err}")
    except Exception as err:
        logging.error(f'[POST] [translate] Failed to process request. {err}')
        raise HTTPException(status_code=500, detail=f"An unknown error occured. Stack trace: {err}")
    if not valid_service:
        logging.error(f'[POST] [translate] Failed to process request. Not valid service {service}')
        raise HTTPException(status_code=400, detail=f"Unknown service: {service}")
    
    # remove backslashes for quotes
    formatted_result = regex.sub(f'\"', "'", result)
    # remove \n
    formatted_result = regex.sub(f'\n', "", formatted_result)
    response.append({
        "service": str(service),
        "target_language": str(target_language),
        "html": f'{formatted_result}'
    })

    logging.info(f'[POST] [translate] Returning with success.')
    return response
