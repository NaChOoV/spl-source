import os
from dotenv import load_dotenv
from utils.decorators import singleton


@singleton
class Config:
    def __init__(self):
        # Prevent re-initialization if already initialized
        if hasattr(self, "_initialized") and self._initialized:
            return

        load_dotenv()

        # API Configuration
        self.API_TITLE = "SPL Source API"
        self.API_VERSION = "0.1.0"
        self.API_DESCRIPTION = (
            "A maintainable FastAPI application with controllers and services"
        )

        # Server Configuration
        self.HOST = os.getenv("HOST", "localhost")
        self.PORT = int(os.getenv("PORT", "4000"))
        self.DEBUG = os.getenv("DEBUG", "true").lower() == "true"

        # Proxy Configuration
        self.HTTP_PROXY = os.getenv("HTTP_PROXY", None)
        self.HTTPS_PROXY = os.getenv("HTTPS_PROXY", None)

        # Authentication Configuration
        self.AUTH_STRING = os.getenv("AUTH_STRING", "mysecretkey123")

        # Source Configuration (existing)
        self.SOURCE_BASE_URL = os.getenv("SOURCE_BASE_URL", "")
        self.SOURCE_USERNAME = os.getenv("SOURCE_USERNAME", "")
        self.SOURCE_PASSWORD = os.getenv("SOURCE_PASSWORD", "")

        # Additional Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

        self._initialized = True


config = Config()
