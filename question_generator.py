import json
import os
import time

from open_ai import OpenAI

# Assistant per textbook or assistant per scenario
# first will be expensive and the instructions should be kept out of the assistant
# - or maybe you can attach multiple files to it?
# - if I upload a file using the API (is this possible), what are my chances linking it to particular assistant or run
# - would it take super long processing time, or it will be the same?

# we will have an issue with the pages and the references.
# It's also very hard for the bot to find the correct pages to fetch the info from

# Maybe if we have the keywords and the pages they're in, in some database, maybe we can fetch the keywords within the
# pages and give them as context to the assistant, which can then use the RAG properly to fetch its information?

# First I should start with generating a **good-looking** test for the whole textbook
# - won't care how it will retrieve and what it will retrieve, I only care about high quality questions
# which I can achieve with the instructions. I won't put chapters or something like that.

# But it's still important to me to have the right answer and references pointing to it for the test evaluation part.

# Then we can promote an exam per chapter approach, which will require a lot more complexity, but we will have
# a greater control over the questions generated and will possibly generate a lot more.


# generated_questions_message = None
# for message_data in messages.data:
#     if 'generatedQuestions' in message_data.content[0].text.value:
#         generated_questions_message = message_data
#         break
#
# generated_questions_content = generated_questions_message.content[0].text.value
# return json.loads(generated_questions_content)
