import logging

from .service import OpenAIService
import time

# Constants
RUN_STATUS_COMPLETED = "completed"
POLL_INTERVAL = 10  # seconds


class OpenAIServiceFacade:
    def __init__(self):
        self.openai_services = OpenAIService()

    def execute_run(self, content, file_ids=None, assistant_id=None):

        # TODO: Reuse threads: when answering questions for the same book and same user or when
        # generating questions for one book (I am not even sure if the user should be the same - it has both pros
        # and cons)

        #TODO: Also if it's one thread make sure that no thread messages before my message are fetched or processed on server side

        thread = self.openai_services.create_thread()

        # Send a message to the thread (with or without file IDs)
        self.openai_services.create_message(thread_id=thread.id, content=content, file_ids=file_ids)

        # Create a run with an optional assistant
        run = self.openai_services.create_run(thread_id=thread.id, assistant_id=assistant_id)
        logging.info(f"Successfully created run: {run}")

        # Poll for the completion of the task
        while run.status != RUN_STATUS_COMPLETED:
            time.sleep(POLL_INTERVAL)
            run = self.openai_services.retrieve_run(thread_id=thread.id, run_id=run.id)
            logging.info(f"Polling run with id: {run.id}, status: {run.status}")

        # Retrieve and return all messages from the thread
        return self.openai_services.list_messages(thread_id=thread.id)
