# 🤖 Agent Workflow Engine

A Streamlit app that lets you schedule and run multi-agent AI workflows using local LLMs via Ollama.

## Features

- **Multi-Agent Pipeline**: Research → Summary → Insight agents run sequentially
- **Scheduler**: Daily, Hourly, or Every-5-min schedules via APScheduler
- **Persistent Storage**: Each run is saved as a JSON session
- **Notifications**: Slack webhook and Email (SMTP) support
- **Dashboard**: View all past run results in the UI

---

## Project Structure

```
agent_workflow_engine/
├── app.py               # Streamlit UI + dashboard
├── scheduler.py         # APScheduler setup
├── workflow_engine.py   # Orchestrates agent pipeline
├── ollama_client.py     # Calls local Ollama LLM
├── storage.py           # Save/load session JSON files
├── notifier.py          # Slack + Email notifications
├── requirements.txt
└── run_sessions/        # Auto-created, stores JSON results
```

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and run Ollama

```bash
# Install Ollama from https://ollama.com
ollama pull llama3        # or: mistral, phi3, gemma, etc.
ollama serve
```

> Edit `ollama_client.py` and change `DEFAULT_MODEL` to match your installed model.

### 3. (Optional) Configure Email notifications

Set environment variables before running:

```bash
export SMTP_EMAIL="you@gmail.com"
export SMTP_PASSWORD="your_app_password"   # Gmail App Password
```

Get a Gmail App Password at: https://myaccount.google.com/apppasswords

### 4. Run the app

```bash
streamlit run app.py
```

---

## How to Use

1. **Sidebar → Schedule Workflow**
   - Enter a workflow name and research topic
   - Choose which agents to run (Research, Summary, Insight)
   - Pick a schedule (Daily / Hourly / Every 5 min / Manual)
   - Optionally add Slack webhook URL or email address
   - Click **Save & Schedule** or **Run Now**

2. **Dashboard**
   - See all active scheduled jobs
   - Browse past run sessions with full agent outputs
   - Delete jobs or clear all results

---

## Adding Custom Agents

Edit `workflow_engine.py` and add a new entry to `AGENT_PROMPTS`:

```python
"MyAgent": (
    "You are a MyAgent. Given topic: {topic}\n"
    "Previous output:\n{previous_output}\n\n"
    "Do something specific..."
),
```

Then select it in the Streamlit multiselect.

---

## Slack Setup

1. Go to https://api.slack.com/messaging/webhooks
2. Create an app and enable Incoming Webhooks
3. Copy the Webhook URL and paste it in the sidebar

---

## Notes

- Scheduled jobs live in memory — they reset if the app restarts. Re-add them after restart.
- Run sessions (JSON files) persist on disk in `run_sessions/`.
- Works fully offline — no external API keys needed (just Ollama running locally).
