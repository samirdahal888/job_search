"""Main entry point for the application"""

import uvicorn

from api_config import api_config
from api_factory import create_app

app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=api_config.API_HOST,
        port=api_config.API_PORT,
        reload=True,
    )
