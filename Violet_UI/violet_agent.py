import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence

from langgraph.graph import END, StateGraph
from langchain_openrouter import ChatOpenRouter
from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()  # reads OPENROUTER_API_KEY from the .env file

# global var storing the document content (server.py swaps it per chat session)
docu_content = ''


class Agent_State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


@tool
def update(content: str) -> str:
    '''Updates the document with the provided content.'''
    global docu_content
    docu_content = content
    return f'Document has been updated successfully! the current content is : \n{docu_content}'


@tool
def save(filename: str) -> str:
    '''Save the current document to a text file and finish the process.

    ARGS :
      filename : name for the text file.
    '''
    global docu_content
    if not filename.endswith('.txt'):
        filename = f'{filename}.txt'
    try:
        os.makedirs('saved_docs', exist_ok=True)
        path = os.path.join('saved_docs', os.path.basename(filename))
        with open(path, 'w') as file:
            file.write(docu_content)
        return f"Document has been saved successfully to '{path}'."
    except Exception as e:
        return f'error in saving the document : {str(e)}'


tools = [update, save]

if not os.getenv('OPENROUTER_API_KEY'):
    raise RuntimeError("OPENROUTER_API_KEY not found. Create a .env file (see .env.example).")

model = ChatOpenRouter(
    model='openrouter/free',
    temperature=0.7,
    openrouter_api_key=os.getenv('OPENROUTER_API_KEY'),
).bind_tools(tools)


def our_agent(state: Agent_State):
    system_prompt = SystemMessage(content=f"""you are a drafter a helpful writting assistant . you are going to help the user update and modify the documents

                                            -if the user wants to update or modify the content  , use the 'update' tool with the complete updated content
                                            -if the user wants to save and finish , you need to use the 'save' tool
                                            -make sure to always show the current document state after modifications

                                            the current document content is : {docu_content}""")
    response = model.invoke([system_prompt] + list(state['messages']))
    return {"messages": [response]}


def after_agent(state: Agent_State) -> str:
    """If the model asked for a tool, run it; otherwise this turn is finished."""
    last = state['messages'][-1]
    return 'tools' if getattr(last, 'tool_calls', None) else 'end'


def after_tools(state: Agent_State) -> str:
    """Same save-detection as your notebook: end once the document is saved."""
    last = state['messages'][-1]
    if isinstance(last, ToolMessage) and 'saved' in last.content.lower() and 'document' in last.content.lower():
        return 'end'
    return 'continue'


graph = StateGraph(Agent_State)
graph.add_node('agent', our_agent)
graph.add_node('tools', ToolNode(tools))
graph.set_entry_point('agent')
graph.add_conditional_edges('agent', after_agent, {'tools': 'tools', 'end': END})
graph.add_conditional_edges('tools', after_tools, {'continue': 'agent', 'end': END})

app = graph.compile()