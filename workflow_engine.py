import time
import uuid
from datetime import datetime
from ollama_client import call_ollama
from storage import save_session
from notifier import send_slack_notification, send_email_notification

# ── Agent prompt templates ─────────────────────────────────────────────────────

AGENT_PROMPTS = {
    "Research": (
        "You are a Research Agent. Your job is to gather and present key facts, "
        "recent developments, and important context about the given topic.\n\n"
        "Topic: {topic}\n\n"
        "Provide a structured research report with bullet points covering:\n"
        "- Key facts and background\n"
        "- Recent developments\n"
        "- Important players or components\n"
        "- Open questions or challenges\n"
        "Be concise but thorough."
    ),
    "Summary": (
        "You are a Summary Agent. You receive research content and distill it "
        "into a crisp, readable executive summary.\n\n"
        "Topic: {topic}\n\n"
        "Research Input:\n{previous_output}\n\n"
        "Write a 3-5 sentence executive summary that captures the most important points. "
        "Use plain language. No bullet points — prose only."
    ),
    "Insight": (
        "You are an Insight Agent. You receive a summary and extract actionable insights, "
        "trends, and recommendations.\n\n"
        "Topic: {topic}\n\n"
        "Summary Input:\n{previous_output}\n\n"
        "Provide:\n"
        "1. Top 3 key insights\n"
        "2. Emerging trends to watch\n"
        "3. Recommended actions or next steps\n"
        "Be specific and practical."
    ),
}


def run_workflow_now(
    workflow_name: str,
    topic: str,
    agents: list,
    slack_webhook: str = "",
    email: str = "",
):
    """
    Runs a multi-agent workflow sequentially.
    Each agent receives the output of the previous one.
    Results are saved to disk.
    """
    session_id = str(uuid.uuid4())[:8]
    run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    steps = []
    previous_output = ""

    print(f"\n[{run_time}] Starting workflow '{workflow_name}' | Session {session_id}")

    for agent_name in agents:
        if agent_name not in AGENT_PROMPTS:
            print(f"  ⚠️  Unknown agent: {agent_name}, skipping.")
            continue

        prompt_template = AGENT_PROMPTS[agent_name]
        prompt = prompt_template.format(topic=topic, previous_output=previous_output)

        print(f"  ▶ Running {agent_name} agent...")
        start = time.time()
        output = call_ollama(prompt)
        duration = round(time.time() - start, 2)
        print(f"  ✅ {agent_name} done in {duration}s")

        steps.append({
            "agent": agent_name,
            "prompt": prompt,
            "output": output,
            "duration_sec": duration,
        })

        previous_output = output  # pass to next agent

    # Build session record
    session = {
        "session_id": session_id,
        "workflow_name": workflow_name,
        "topic": topic,
        "agents": agents,
        "run_time": run_time,
        "steps": steps,
    }

    save_session(session)
    print(f"  💾 Session {session_id} saved.\n")

    # Notifications
    final_output = steps[-1]["output"] if steps else "No output."
    notification_text = (
        f"✅ Workflow '{workflow_name}' completed at {run_time}\n"
        f"Topic: {topic}\n\n"
        f"Final Insight:\n{final_output[:800]}"
    )

    if slack_webhook:
        send_slack_notification(slack_webhook, notification_text)

    if email:
        send_email_notification(email, f"Workflow '{workflow_name}' Results", notification_text)

    return session
