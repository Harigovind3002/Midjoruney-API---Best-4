from fastapi import FastAPI, HTTPException, Form
import requests

app = FastAPI()

MIDJOURNEY_API_URL = "https://api.userapi.ai/midjourney/v2"
MIDJOURNEY_API_KEY = "81ffded2-61b6-4f25-a75f-49a11ff2478b"

@app.post("/imagine")
async def imagine(
    prompt: str = Form(...),
    webhook_url: str = Form(None),
    webhook_type: str = Form("result"),
    account_hash: str = Form(None),
    is_disable_prefilter: bool = Form(False),
):
    all_urls = []
    for _ in range(4):
        urls=[]
        url = f"{MIDJOURNEY_API_URL}/imagine"
        headers = {
            "api-key": MIDJOURNEY_API_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "prompt": prompt,
            "webhook_url": webhook_url,
            "webhook_type": webhook_type,
            "account_hash": account_hash,
            "is_disable_prefilter": is_disable_prefilter,
        }
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        task_hash = response_data.get("hash")
        status_url = f"{MIDJOURNEY_API_URL}/status?hash={task_hash}"
        while True:
            status_response = requests.get(status_url, headers=headers)
            status_response_data = status_response.json()
            if status_response_data.get("status") == "done":
                upscale_url = f"{MIDJOURNEY_API_URL}/upscale"
                headers = {
                    "api-key": MIDJOURNEY_API_KEY,
                    "Content-Type": "application/json"
                }   
                data = {
                    "hash": task_hash,
                    "choice": 1,
                    "webhook_url": webhook_url,
                    "webhook_type": webhook_type,
                }
                upscale_response = requests.post(upscale_url, headers=headers, json=data)
                upscale_response_data = upscale_response.json()
                upscale_hash = upscale_response_data.get("hash")
                upscale_status_url = f"{MIDJOURNEY_API_URL}/status?hash={upscale_hash}"
                while True:
                    upscale_status_response = requests.get(upscale_status_url, headers=headers)
                    upscale_status_response_data = upscale_status_response.json()
                    if upscale_status_response_data.get("status") == "done":
                        task_urls = upscale_status_response_data.get("result", {}).get("url")
                        print(task_urls)
                        urls.append(task_urls)
                    break
                all_urls.append(urls)
                break
    return {"all_urls":all_urls}
            