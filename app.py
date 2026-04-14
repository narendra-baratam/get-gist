from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

GITHUB_API_BASE = "https://api.github.com"
GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


@app.get("/{username}")
async def get_user_gists(username: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API_BASE}/users/{username}/gists",
            headers=GITHUB_HEADERS,
        )
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    if response.status_code == 429:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded for user '{username}'")
    if response.is_error:
        raise HTTPException(response.status_code, detail=f"User '{username}' GitHub API error")
    return response.json()
