from .client import OpenAIClient


class OpenAIService:
    def __init__(self):
        self.client = OpenAIClient().client

    def create_thread(self):
        return self.client.beta.threads.create()

    def create_message(self, thread_id, content, file_ids=None):
        message_data = {
            "thread_id": thread_id,
            "role": "user",
            "content": content
        }
        if file_ids:
            message_data["file_ids"] = file_ids
        return self.client.beta.threads.messages.create(**message_data)

    def create_run(self, thread_id, assistant_id=None):
        run_data = {"thread_id": thread_id}
        if assistant_id:
            run_data["assistant_id"] = assistant_id

        return self.client.beta.threads.runs.create(**run_data)

    def retrieve_run(self, thread_id, run_id):
        return self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)

    def list_messages(self, thread_id):
        return self.client.beta.threads.messages.list(thread_id=thread_id)

    def create_file(self, file):
        return self.client.files.create(file=file, purpose="assistants")
