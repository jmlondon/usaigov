from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()

# Your verified base domain and full path segment
BASE_URL = "https://api.doc.usai.gov/api/v1"

@app.get("/v1/models")
async def list_models():
    """
    Returns your exact model catalog in the strict OpenAI structure 
    that Positron requires, ensuring the dropdown works flawlessly.
    """
    return {
        "object": "list",
        "data": [
            {
                "id": "gpt-5.4-latest-guardrails-defaultv2",
                "object": "model",
                "created": 1715000000,
                "owned_by": "Open AI"
            },
            {
                "id": "claude_3_5_haiku",
                "object": "model",
                "created": 1715000000,
                "owned_by": "Anthropic"
            },
            {
                "id": "gemini-2.5-flash",
                "object": "model",
                "created": 1715000000,
                "owned_by": "Google"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def relay_chat(request: Request):
    """
    Forwards chat generation requests using the explicit /api/v1 path pattern.
    """
    body = await request.json()
    headers = dict(request.headers)
    
    # Ensure streaming format is strictly on
    body["stream"] = True

    forward_headers = {
        "Authorization": headers.get("authorization"),
        "Content-Type": "application/json"
    }

    async def stream_generator():
        async with httpx.AsyncClient() as client:
            try:
                # Direct tunnel to the complete, correct USAi path
                async with client.stream(
                    "POST", 
                    f"{BASE_URL}/chat/completions", 
                    json=body, 
                    headers=forward_headers,
                    timeout=60.0
                ) as r:
                    async for chunk in r.aiter_text():
                        if chunk:
                            yield chunk
            except httpx.ConnectError:
                yield "data: {\"error\": {\"message\": \"Proxy cannot reach gateway. Check your VPN.\"}}\n\n"
                yield "data: [DONE]\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)