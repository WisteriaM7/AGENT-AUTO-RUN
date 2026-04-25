import streamlit as st
import json
import time
from datetime import datetime
from pathlib import Path
from scheduler import start_scheduler, get_scheduler
from workflow_engine import run_workflow_now
from storage import load_all_sessions, load_session, clear_all_sessions
from notifier import send_slack_notification, send_email_notification

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agent Workflow Engine",
    page_icon="🤖",
    layout="wide",
)

# ── Ensure scheduler is running ───────────────────────────────────────────────
if "scheduler_started" not in st.session_state:
    start_scheduler()
    st.session_state.scheduler_started = True

# ── Sidebar – Schedule a new workflow ─────────────────────────────────────────
with st.sidebar:
    st.title("🤖 Workflow Engine")
    st.divider()

    st.subheader("➕ Schedule Workflow")

    workflow_name = st.text_input("Workflow Name", value="Morning Briefing")
    topic = st.text_input("Research Topic", value="AI and machine learning news")

    agents = st.multiselect(
        "Agents (in order)",
        ["Research", "Summary", "Insight"],
        default=["Research", "Summary", "Insight"],
    )

    schedule_type = st.selectbox("Schedule", ["Daily", "Hourly", "Every 5 min (demo)", "Manual Only"])
    run_hour = st.slider("Run at hour (for Daily)", 0, 23, 8) if schedule_type == "Daily" else None

    notify_slack = st.checkbox("Notify via Slack")
    slack_webhook = ""
    if notify_slack:
        slack_webhook = st.text_input("Slack Webhook URL", type="password")

    notify_email = st.checkbox("Notify via Email")
    email_address = ""
    if notify_email:
        email_address = st.text_input("Email Address")

    st.divider()

    if st.button("💾 Save & Schedule", use_container_width=True):
        if not workflow_name or not topic or not agents:
            st.error("Please fill in all fields.")
        else:
            scheduler = get_scheduler()
            job_config = {
                "workflow_name": workflow_name,
                "topic": topic,
                "agents": agents,
                "slack_webhook": slack_webhook if notify_slack else "",
                "email": email_address if notify_email else "",
            }

            job_id = f"job_{workflow_name.replace(' ', '_').lower()}"

            # Remove old job if exists
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)

            if schedule_type == "Daily":
                scheduler.add_job(
                    run_workflow_now,
                    "cron",
                    hour=run_hour,
                    minute=0,
                    id=job_id,
                    kwargs=job_config,
                    replace_existing=True,
                )
            elif schedule_type == "Hourly":
                scheduler.add_job(
                    run_workflow_now,
                    "interval",
                    hours=1,
                    id=job_id,
                    kwargs=job_config,
                    replace_existing=True,
                )
            elif schedule_type == "Every 5 min (demo)":
                scheduler.add_job(
                    run_workflow_now,
                    "interval",
                    minutes=5,
                    id=job_id,
                    kwargs=job_config,
                    replace_existing=True,
                )

            st.success(f"✅ Workflow '{workflow_name}' scheduled!")

    if st.button("▶️ Run Now", use_container_width=True):
        if not workflow_name or not topic or not agents:
            st.error("Please fill in all fields.")
        else:
            with st.spinner("Running workflow..."):
                job_config = {
                    "workflow_name": workflow_name,
                    "topic": topic,
                    "agents": agents,
                    "slack_webhook": slack_webhook if notify_slack else "",
                    "email": email_address if notify_email else "",
                }
                run_workflow_now(**job_config)
            st.success("✅ Workflow complete!")
            st.rerun()

    st.divider()
    st.subheader("🗑️ Manage")
    if st.button("Clear All Results", use_container_width=True):
        clear_all_sessions()
        st.success("Cleared.")
        st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("📊 Agent Workflow Dashboard")
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Active scheduled jobs
scheduler = get_scheduler()
jobs = scheduler.get_jobs()

st.subheader("⏰ Scheduled Jobs")
if jobs:
    for job in jobs:
        next_run = job.next_run_time
        next_run_str = next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else "N/A"
        col1, col2, col3 = st.columns([3, 3, 1])
        col1.markdown(f"**{job.id}**")
        col2.markdown(f"Next run: `{next_run_str}`")
        if col3.button("❌", key=f"del_{job.id}"):
            scheduler.remove_job(job.id)
            st.rerun()
else:
    st.info("No scheduled jobs. Use the sidebar to add one.")

st.divider()

# Past run results
st.subheader("📋 Past Run Sessions")
sessions = load_all_sessions()

if not sessions:
    st.info("No runs yet. Schedule or manually run a workflow.")
else:
    for session in reversed(sessions):
        session_id = session.get("session_id", "unknown")
        wf_name = session.get("workflow_name", "Workflow")
        run_time = session.get("run_time", "")
        topic = session.get("topic", "")

        with st.expander(f"🗂 {wf_name} — {run_time}  |  Topic: {topic}", expanded=False):
            steps = session.get("steps", [])
            for step in steps:
                agent = step.get("agent")
                output = step.get("output", "")
                duration = step.get("duration_sec", 0)
                st.markdown(f"### 🔹 {agent} Agent")
                st.markdown(f"*Duration: {duration:.1f}s*")
                st.markdown(output)
                st.divider()

# Auto-refresh every 30 seconds
time.sleep(0)
if st.button("🔄 Refresh Dashboard"):
    st.rerun()
