from fastapi import Request, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

# Path to your dist folder
DIST_FOLDER = Path("./dist")

router = APIRouter()

# Mount static files (CSS, JS, images, etc.) to the router
router.mount("/assets", StaticFiles(directory=DIST_FOLDER / "assets"), name="assets")

# Serve other static files individually
@router.get("/icon.png")
async def get_icon():
    return FileResponse(DIST_FOLDER / "icon.png")

@router.get("/manifest.json")
async def get_manifest():
    return FileResponse(DIST_FOLDER / "manifest.json")

@router.get("/sw.js")
async def get_service_worker():
    return FileResponse(DIST_FOLDER / "sw.js", media_type="application/javascript")

# Root route for the React app
@router.get("/")
async def root():
    return FileResponse(DIST_FOLDER / "index.html")

# Catch-all route for React Router (SPA)
@router.get("/{full_path:path}")
async def serve_react_app(request: Request, full_path: str):
    """
    Serve the React app for all routes.
    This enables client-side routing to work properly.
    """
    # Check if the requested file exists in dist folder
    file_path = DIST_FOLDER / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    
    # For all other routes, serve index.html (SPA behavior)
    return FileResponse(DIST_FOLDER / "index.html")