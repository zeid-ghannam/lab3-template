import multiprocessing

from src import create_app
from src.queue.worker import RetryWorker

import logging

logger = logging.getLogger(__name__)


def start_worker():
    worker = RetryWorker()
    worker.start()


def main():
    # Start the worker in a separate process
    worker_process = multiprocessing.Process(target=start_worker)
    worker_process.start()
    logger.info("Started retry worker process")

    # Start the Flask app
    app = create_app()
    app.run(host="0.0.0.0", port=8080,debug=True)


if __name__ == "__main__":
    main()
