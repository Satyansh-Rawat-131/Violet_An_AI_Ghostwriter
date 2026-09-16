# Violet — An AI Ghostwriter 🖋️

Violet is a human-in-the-loop AI agent that drafts, revises, and saves documents through natural back-and-forth conversation, built with **LangGraph** and **LangChain**. It's designed to solve a simple problem: teams spend too much time manually drafting documents, emails, and notes when an AI collaborator could do the heavy lifting while the human stays in control.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Satyansh-Rawat-131/Violet_An_AI_Ghostwriter/blob/main/VIOLET.ipynb)

## The Problem

Drafting documents and emails from scratch is slow, and handing the job entirely to an AI removes the human's control over tone, content, and correctness. Violet is built around **human–AI collaboration**: the agent drafts and edits based on continuous human feedback, and only stops once the human is satisfied with the result and explicitly asks to save.

## How It Works

Violet is implemented as a **stateful agent graph** using LangGraph, with two nodes that loop until the document is finalized:

- **`agent` node** — sends the conversation (system prompt + history + latest user input) to the LLM and decides whether to update the document or save it.
- **`tools` node** — executes the tool the agent picked.

**Tools available to the agent:**
| Tool | Purpose |
|---|---|
| `update(content)` | Overwrites the in-memory document with new/edited content |
| `save(filename)` | Writes the current document to a `.txt` file and ends the session |

**Control flow:**
1. The agent greets the user and asks what they'd like to draft.
2. On each turn, the user gives feedback or instructions via input.
3. The agent calls `update` to revise the document, or `save` when the user is happy with it.
4. A conditional edge (`should_continue`) checks the latest tool result — if it was a successful `save`, the graph routes to `END`; otherwise it loops back to the `agent` node for another round of feedback.

This gives a simple but effective **draft → review → revise → save** loop, entirely driven by human feedback.

## Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** — stateful graph orchestration for the agent loop
- **[LangChain](https://github.com/langchain-ai/langchain)** — messages, tool definitions, and tool-calling model binding
- **[OpenRouter](https://openrouter.ai/)** (via `langchain-openrouter`) — LLM backend
- **Python** — runs as a single Google Colab notebook

## Getting Started

### 1. Open the notebook
Click the **Open in Colab** badge above, or open [`VIOLET.ipynb`](./VIOLET.ipynb) directly.

### 2. Add your API key
Violet uses OpenRouter as its model provider. In Colab, add your key as a secret named `API_KEY`:

```
Colab → 🔑 Secrets panel → New secret → Name: API_KEY → Value: <your OpenRouter API key>
```

### 3. Run all cells
This installs `langchain-openrouter`, builds the agent graph, and compiles the app.

### 4. Start drafting
Run the final cell to launch the interactive loop:

```python
if __name__ == "__main__":
    run_document_agent()
```

Then just talk to Violet — ask it to draft something, give feedback to revise it, and tell it to save when you're done. The finished document is written out as a `.txt` file.

## Example Session

```
===== DRAFTER =====
🤖 AI: I am ready to help you update a document. What would you like to create?

What would you like to do with the document? Draft a short email announcing our new product launch
🤖 AI: Here's a draft for you...
🔧 USING TOOLS: ['update']

What would you like to do with the document? Make it more casual and save it as launch_email
🤖 AI: Updated the tone and saved the document.
🔧 USING TOOLS: ['update', 'save']

===== DRAFTER FINISHED =====
```

## Project Structure

```
Violet_An_AI_Ghostwriter/
├── VIOLET.ipynb   # Full implementation: agent, tools, graph, and run loop
└── README.md
```

## Possible Improvements

- [ ] Persist document versions/history instead of overwriting in memory
- [ ] Support richer file formats (`.docx`, `.md`) beyond plain `.txt`
- [ ] Add a lightweight UI (e.g. Streamlit) instead of console `input()`
- [ ] Swap the free OpenRouter model for a configurable model choice
- [ ] Add undo/redo for document edits

## Author

**Satyansh Rawat**
[GitHub](https://github.com/Satyansh-Rawat-131)
