from qa_over_docs.apis.base import BaseAPI, ChatResponse
import openai, tiktoken, json
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()

SYSTEM_INSTRUCTIONS = '''
Answer the user's question based on the given context.
Return your response in JSON like this:

{
    "relevant_source_ids": [],
    "answer": ...
}

where "relevant_source_ids" is a list of {SOURCE ID} of the sources
relevant to the user's question. "answer" is your response to the user's
question based on the context. For example:

{
    "relevant_source_ids": ["443350746039594436", "443350746039594128"],
    "answer": "The answer to your question is..."
}
'''

USER_REMINDER = '''
Please remember to respond in JSON shown before and to use '\\n' for newlines.
Also remember to provide the source ids of all relevant sources. Ensure you
retrieve back ALL source ids whether the content is relevant to the user's question.
Do not mention the source ids in "answer".
Thank you.
'''

MAX_TOKEN_LENGTH = 3700

class OpenAI(BaseAPI):
    def __init__(self) -> None:
        super().__init__(SYSTEM_INSTRUCTIONS, USER_REMINDER, MAX_TOKEN_LENGTH)


    def num_tokens_from_string(self, string: str) -> int:
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(string))
        return num_tokens
    

    def retrieve_response(self, question: str, relevant_docs: list[dict]) -> ChatResponse:
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "system", "content": "CONTEXT: \n\n\n\n"},
            {"role": "user", "content": f"{question}\n\n{USER_REMINDER}"}
        ]

        base_token_length = self.get_messages_token_length(messages)

        context = ""

        for doc in relevant_docs:
            new_context = context
            new_context += "\n\n\n" + "{SOURCE ID}: " +  str(doc["pk"]) + "\n" + doc["text"]

            if self.num_tokens_from_string(new_context) > self.max_token_length - base_token_length:
                break

            context = new_context

        messages[1]["content"] += context

        pprint(messages)

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        response_string = completion.choices[0].message.content.strip()
        print(response_string)
        
        response: dict
        try:
            response = json.loads(response_string)
            response["relevant_source_ids"] = [int(source_id) for source_id in response["relevant_source_ids"]]
        except Exception as e:
            print(f"{str(e)}\nCouldn't parse model's response as JSON:\n{response_string}")
            response = {
                "relevant_source_ids": [],
                "answer": response_string
            }
        response: ChatResponse = response

        return response