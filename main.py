import uvicorn
from config.env import config
import logging


def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("MAIN")
    logger.info("Starting the application...")

    """Run the FastAPI server"""
    uvicorn.run("app.main:app", host=config.HOST, port=config.PORT, reload=config.DEBUG)


if __name__ == "__main__":
    main()
