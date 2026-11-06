
import datetime
import requests

OLLAMA_API = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:0.5b"

conversation_history=[]


# Python tools

def get_current_date():
    return datetime.date.today().strftime("%d-%m-%Y")


def get_current_time():
    return datetime.datetime.now().strftime("%I:%M %p")


# Tell Qwen which tools are available

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "Get today's current date",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get the current time",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


# Connect Python with Qwen

def ask_ai(question):


    conversation_history.append({
        "role": "user",
        "content": question
    })

    messages = conversation_history

    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOLS,
        "stream": False
    }

    try:
        # First request: Ask Qwen to decide which tool to use
        response = requests.post(
            OLLAMA_API,
            json=payload,
            timeout=120
        )

        response.raise_for_status()
        result = response.json()

        message = result["message"]
        tool_calls = message.get("tool_calls", [])

        # If Qwen doesn't request a tool, return its answer
        if not tool_calls:
            final_answer=message.get("content","")
            conversation_history.append({
            "role": "assistant",
            "content": final_answer 

            })
            return final_answer

        # Add Qwen's tool request to conversation history
        messages.append(message)

        # Execute the requested Python functions
        for tool_call in tool_calls:

            tool_name = tool_call["function"]["name"]

            if tool_name == "get_current_date":
                tool_result = get_current_date()

            elif tool_name == "get_current_time":
                tool_result = get_current_time()

            else:
                tool_result = "Unknown tool"

            print(f"Executing tool: {tool_name}")

            # Send Python's result back to Qwen
            messages.append({
                "role": "tool",
                "name": tool_name,
                "content": str(tool_result)
            })

        # Second request: Qwen explains the tool result
        response = requests.post(
            OLLAMA_API,
            json={
                "model": MODEL,
                "messages": messages,
                "tools": TOOLS,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        result = response.json()

        final_answer = result["message"].get("content", "")
        
        conversation_history.append({
        "role": "assistant",
        "content": final_answer

        })
        return final_answer

    except requests.exceptions.RequestException as error:
        return f"Error connecting to AI: {error}"

# Main assistant

def assistant():

    print("==============================")
    print("    AI PERSONAL ASSISTANT")
    print("==============================")
    print("Ask me anything!")
    print("Type 'exit' to stop.\n")

    while True:

        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Assistant: Goodbye!")
            break

        if not user_input:
            continue

        answer = ask_ai(user_input)

        print("\nAssistant:", answer, "\n")


if __name__ == "__main__":
    assistant()

