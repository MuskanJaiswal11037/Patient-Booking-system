import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
from typing import Optional, Dict, List, Tuple, Any
from components.api import (
    get_appointment_details,
    update_queue_appointment_status,
    get_waiting_list,
    get_emergency_appointments,
    get_queue_doctors,
    create_emergency_appointment_quick,
)
from components.utils import get_state_manager
from streamlit_autorefresh import st_autorefresh



_QUEUE_PAGE_CSS = """
<style>
body, .stApp {
    background-color: #0f1115 !important;
    color: #e6e6e6 !important;
}
body, .stApp {
    background-color: #0f1115 !important;
    color: #e6e6e6 !important;
}
.main {
    padding: 0rem 1rem;
    background: transparent !important;
    background: transparent !important;
}
.stMetric {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.35);
    box-shadow: 0 2px 10px rgba(0,0,0,0.35);
}
.stMetric label {
    color: rgba(255,255,255,0.85);
    color: rgba(255,255,255,0.85);
}
.queue-card {
    border-left: 4px solid #667eea;
    padding: 1rem;
    border-radius: 0.5rem;
    background: #171a22;
    background: #171a22;
    margin-bottom: 1rem;
}
.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: bold;
}
.status-scheduled {
    background-color: #667eea;
    color: white;
}
.status-in-progress {
    background-color: #ffc107;
    color: #111214;
    color: #111214;
}
.status-completed {
    background-color: #28a745;
    color: white;
}
.status-no-show {
    background-color: #dc3545;
    color: white;
}
/* Button Styles */
.stButton > button {
    background-color: #1f77b4 !important;
    color: white !important;
    border: 1px solid #1f77b4 !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background-color: #1557a0 !important;
    border-color: #1557a0 !important;
}
/* Form Submit Buttons */
.stFormSubmitButton > button {
    background-color: #28a745 !important;
    color: white !important;
    border: 1px solid #28a745 !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
}
.stFormSubmitButton > button:hover {
    background-color: #218838 !important;
    border-color: #218838 !important;
}
/* App Header */
.stAppHeader {
    background-color: #0f1115 !important;
}
/* Button Styles */
.stButton > button {
    background-color: #1f77b4 !important;
    color: white !important;
    border: 1px solid #1f77b4 !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background-color: #1557a0 !important;
    border-color: #1557a0 !important;
}
/* Form Submit Buttons */
.stFormSubmitButton > button {
    background-color: #28a745 !important;
    color: white !important;
    border: 1px solid #28a745 !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
}
.stFormSubmitButton > button:hover {
    background-color: #218838 !important;
    border-color: #218838 !important;
}
/* App Header */
.stAppHeader {
    background-color: #0f1115 !important;
}
</style>
"""

def _apply_queue_page_styles() -> None:
    """Inject custom CSS; must run inside a page function, not at import time."""
    st.markdown(_QUEUE_PAGE_CSS, unsafe_allow_html=True)

# ==================== UTILITIES ====================

def get_status_color(status: str) -> str:
    """Get color for status"""
    colors = {
        'scheduled': '🔵',
        'in-progress': '🟡',
        'completed': '🟢',
        'no-show': '🔴'
    }
    return colors.get(status, '⚪')


# ==================== APPOINTMENT FUNCTIONS ====================

@st.cache_data(ttl=10)
def _appointments_df_cached(doctor_email: str, status_key: str) -> pd.DataFrame:
    rows = get_appointment_details(
        doctor_email= None,
        status="All",
    )
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if status_key != "All":
        df = df[df["status"] == status_key]
    if doctor_email:
        df = df[df["doctor_email"] == doctor_email]
    return df;


def get_appointments_cached(
    doctor_email: str = "",
    status: Optional[str] = None,
) -> pd.DataFrame:
    """Load appointments from backend (cached briefly)."""
    status_key = status if status else "All"
    df = _appointments_df_cached(doctor_email, status_key)
    if df.empty:
        return df
    if "queue_position" in df.columns:
        df = df.sort_values(
            by=["queue_position"],
            na_position="last",
        )

    return df


def update_appointment_status(apt_id: Any, new_status: str, notes: str = None) -> Tuple[bool, str]:
    """Update appointment status via backend."""
    ok = update_queue_appointment_status(str(apt_id), new_status)
    if ok:
        st.cache_data.clear()
        return True, "Status updated successfully"
    return False, "Update failed"


# ==================== STATISTICS ====================

def get_queue_stats(doctor_email: str) -> Dict[str, int]:
    """Get queue statistics from backend data."""
    df = get_appointments_cached(doctor_email, "All")
    if df.empty:
        return {
            "total": 0,
            "scheduled": 0,
            "in_progress": 0,
            "completed": 0,
            "no_show": 0,
        }
    return {
        "total": len(df),
        "scheduled": int((df["status"] == "scheduled").sum()) if "status" in df else 0,
        "in_progress": int((df["status"] == "in-progress").sum()) if "status" in df else 0,
        "completed": int((df["status"] == "completed").sum()) if "status" in df else 0,
        "no_show": int((df["status"] == "no_show").sum()) if "status" in df else 0,
        "cancelled": int((df["status"] == "cancelled").sum()) if "status" in df else 0,
    }


def _parse_ts(s: Optional[str]) -> Optional[pd.Timestamp]:
    if not s:
        return None
    t = pd.to_datetime(s, errors="coerce")
    return None if pd.isna(t) else t


def get_avg_wait_time(doctor_email: str) -> int:
    """Average wait (minutes) for completed visits when check-in/out exist."""
    df = get_appointments_cached(doctor_email, "All")
    if df.empty or "status" not in df.columns:
        return 0
    done = df[df["status"] == "completed"]
    mins: List[float] = []
    for _, a in done.iterrows():
        ci, co = _parse_ts(a.get("checkin_time")), _parse_ts(a.get("checkout_time"))
        if ci is not None and co is not None:
            delta = (co - ci).total_seconds() / 60.0
            if delta >= 0:
                mins.append(delta)
    return int(sum(mins) / len(mins)) if mins else 0


def analyze_busiest_doctor() -> Dict[str, Any]:
    """
    Analyze and identify the busiest doctor based on multiple metrics.
    
    Returns:
        Dictionary containing:
        - busiest_doctor: Doctor with most appointments
        - doctors_analysis: List of doctors with their metrics
        - avg_workload: Average appointments per doctor
    """
    df = get_appointments_cached("", "All")
    
    if df.empty:
        return {
            "success": False,
            "message": "No appointment data available",
            "busiest_doctor": None,
            "doctors_analysis": [],
            "avg_workload": 0
        }
    
    # Group by doctor to get appointment counts
    doctor_stats = df.groupby("doctor_email").agg({
        "id": "count",
        "doctor_name": "first",
        "status": lambda x: x.value_counts().to_dict()
    }).reset_index()
    
    doctor_stats.columns = ["doctor_email", "total_appointments", "doctor_name", "status_breakdown"]
    
    # Calculate additional metrics per doctor
    doctors_analysis = []
    for _, row in doctor_stats.iterrows():
        doctor_email = row["doctor_email"]
        doctor_df = df[df["doctor_email"] == doctor_email]
        
        # Count patients (unique)
        unique_patients = doctor_df["patient_id"].nunique() if "patient_id" in doctor_df.columns else 0
        
        # Completed appointments
        completed = len(doctor_df[doctor_df["status"] == "completed"]) if "status" in doctor_df.columns else 0
        
        # In progress
        in_progress = len(doctor_df[doctor_df["status"] == "in-progress"]) if "status" in doctor_df.columns else 0
        
        # Calculate average wait time for this doctor
        avg_wait = get_avg_wait_time(doctor_email)
        
        # Busiest hour
        if "appointment_at" in doctor_df.columns:
            doctor_df_copy = doctor_df.copy()
            doctor_df_copy["hour"] = pd.to_datetime(doctor_df_copy["appointment_at"], errors="coerce").dt.hour
            busiest_hour = doctor_df_copy["hour"].mode()[0] if not doctor_df_copy["hour"].mode().empty else None
        else:
            busiest_hour = None
        
        doctor_info = {
            "doctor_email": doctor_email,
            "doctor_name": row["doctor_name"],
            "total_appointments": int(row["total_appointments"]),
            "unique_patients": unique_patients,
            "completed_appointments": completed,
            "in_progress_appointments": in_progress,
            "average_wait_time_minutes": avg_wait,
            "busiest_hour": busiest_hour,
            "efficiency_score": round((completed / row["total_appointments"] * 100), 2) if row["total_appointments"] > 0 else 0
        }
        doctors_analysis.append(doctor_info)
    
    # Sort by total appointments (descending)
    doctors_analysis.sort(key=lambda x: x["total_appointments"], reverse=True)
    
    # Get busiest doctor
    busiest_doctor = doctors_analysis[0] if doctors_analysis else None
    
    # Calculate average workload
    avg_workload = round(df.groupby("doctor_email").size().mean(), 2)
    
    return {
        "success": True,
        "busiest_doctor": busiest_doctor,
        "doctors_analysis": doctors_analysis,
        "avg_workload": avg_workload
    }

def _render_busiest_doctor_analysis() -> None:
    """Render busiest doctor analysis dashboard."""
    st.markdown("### 👨‍⚕️ Doctor Workload Analysis")
    
    analysis = analyze_busiest_doctor()
    
    if not analysis["success"]:
        st.warning(analysis.get("message", "No data available"))
        return
    
    # Display key metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("📊 Avg Workload", f"{analysis['avg_workload']} appts")
    with col2:
        st.metric("👨‍⚕️ Total Doctors", len(analysis['doctors_analysis']))
    
    st.divider()
    
    # Busiest Doctor Highlight
    if analysis["busiest_doctor"]:
        busiest = analysis["busiest_doctor"]
        st.markdown(f"#### 👨‍⚕️ Busiest Doctor: {busiest['doctor_name']}")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Appts", busiest["total_appointments"])
        with col2:
            st.metric("Unique Patients", busiest["unique_patients"])
        with col3:
            st.metric("Completed", busiest["completed_appointments"])
        with col4:
            st.metric("In Progress", busiest["in_progress_appointments"])
        with col5:
            st.metric("Efficiency %", f"{busiest['efficiency_score']}%")
        
        if busiest["average_wait_time_minutes"] > 0:
            st.info(f"⏱️ Average Wait Time: {busiest['average_wait_time_minutes']} minutes")
        
        # if busiest["busiest_hour"]:
        #     st.info(f"⏰ Peak Hour: {busiest['busiest_hour']:02d}:00")
    
    st.divider()
    
    # Doctor comparison chart
    st.markdown("#### 📊 Doctor Comparison")
    
    doctors_df = pd.DataFrame(analysis["doctors_analysis"])
    
    if not doctors_df.empty:
        
        # Efficiency score comparison
        col1, col2 = st.columns(2)
        
        with col1:
            fig2 = px.bar(
                doctors_df.sort_values("efficiency_score", ascending=False),
                x="doctor_name",
                y="efficiency_score",
                title="Efficiency Score (% Completed)",
                color="efficiency_score",
                color_continuous_scale="Greens",
                labels={"efficiency_score": "Efficiency %", "doctor_name": "Doctor"}
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            # Workload comparison
            fig1 = px.bar(
                doctors_df.sort_values("total_appointments", ascending=False),
                x="doctor_name",
                y="total_appointments",
                title="Total Appointments per Doctor",
                color="total_appointments",
                color_continuous_scale="Blues",
                labels={"total_appointments": "Appointments", "doctor_name": "Doctor"}
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)



def _render_overview_tab(doctor_email: str) -> None:
    st.subheader("📈 Appointments Overview")
    stats = get_queue_stats(doctor_email)
    avg_wait = get_avg_wait_time(doctor_email)

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("📊 Total", stats["total"])
    with col2:
        st.metric("🔵 Scheduled", stats["scheduled"])
    with col3:
        st.metric("🟡 In Progress", stats["in_progress"])
    with col4:
        st.metric("🟢 Completed", stats["completed"])
    with col5:
        st.metric("🔴 No Show", stats["no_show"])
    with col6:
        st.metric("⚪ CANCELLED", stats["cancelled"])

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Scheduled", "In Progress", "Completed", "No Show", "CANCELLED"],
                    values=[
                        stats["scheduled"],
                        stats["in_progress"],
                        stats["completed"],
                        stats["no_show"],
                        stats["cancelled"]
                    ],
                    marker=dict(colors=["#667eea", "#ffc107", "#28a745", "#dc3545", "#fff5f5e9"]),
                )
            ]
        )
        fig.update_layout(title="Status Distribution", height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df = get_appointments_cached(doctor_email, "All")
        if not df.empty:
            df["hour"] = pd.to_datetime(df["appointment_at"]).dt.hour
            hourly = df.groupby("hour").size().reset_index(name="count")
            fig = px.bar(
                hourly,
                x="hour",
                y="count",
                title="Appointments by Hour",
                color="count",
                color_continuous_scale="Blues",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    st.divider()
    _render_busiest_doctor_analysis()

    if st.button("🔄 Refresh All Data", key="refresh_overview_tab"):
        st.cache_data.clear()
        st.rerun()



def _render_update_appointments_tab(user, doctor_email: str) -> None:
    st.subheader("All Appointments")

    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "scheduled", "in-progress", "completed", "no_show", "cancelled"],
            key="upd_appt_status",
        )
    with col2:
        doctor_email = st.text_input("Doctor Email", key="upd_appt_doctor_email")
    with col3:
        if st.button("🔄 Refresh", key="refresh_upd_appt"):
            st.cache_data.clear()
            st.rerun()

    df = get_appointments_cached(doctor_email, status_filter)
    if not df.empty:
        st.write(f"**{len(df)} appointments found**")

        for _, row in df.iterrows():
            with st.container(border=True):
                col1, col2, col4, col5 = st.columns([2, 1.5,1.5, 1])

                with col1:
                    # st.write(f"**#{row['queue_position']} - {row['patient_name']}**")
                    st.write(f"� Patient: {row.get('patient_name') or row['patient_id'] or 'N/A'}")

                with col2:
                    st.write(f"⏰ {row['appointment_at']}")
                    st.write(f"👨‍⚕️ Doctor: {row.get('doctor_name') or row.get('doctor_id') or 'N/A'}")


                with col4:
                    emoji = get_status_color(row["status"].strip().lower())
                    st.write(f"{emoji} {row['status'].upper()}")

                with col5:
                    if st.button("Update", key=f"update_{row['id']}"):
                        st.session_state.selected_apt = row["id"]

            if "selected_apt" in st.session_state and st.session_state.selected_apt == row["id"]:
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_status = st.selectbox(
                        "New Status",
                        ["in-progress", "completed", "no_show", "cancelled", "scheduled"],
                        key=f"newstat_{row['id']}",
                    )
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ Update", key=f"confirm_{row['id']}"):
                        print(f"Updating appointment {row['id']} to status {new_status}")
                        success, msg = update_appointment_status(row["id"], new_status)
                        if success:
                            st.success(msg)
                            del st.session_state.selected_apt
                            st.cache_data.clear()
                            st.rerun()
                with col_b:
                    if st.button("✗ Cancel", key=f"cancel_{row['id']}"):
                        del st.session_state.selected_apt
                        st.rerun()
    else:
        st.info("No appointments found")


def _render_live_queue_tab(doctor_email: str) -> None:
    df_all = get_appointments_cached(doctor_email, "All")
    if df_all.empty:
        st.warning(" (check backend data or doctor filter).")
        return

    if st.button("🔄 Refresh Queue", key="refresh_live_queue"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    df = get_appointments_cached(doctor_email, "All")

    if df.empty:
        st.info("No appointments available..")
        return

    waiting = get_waiting_list()
    if waiting:
        waiting = pd.DataFrame(waiting)
    else:
        waiting = pd.DataFrame()
    serving = df[df["status"] == "in-progress"]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", len(df))
    with col2:
        st.metric("Waiting", len(waiting))
    with col3:
        st.metric("Being Served", len(serving))

    st.divider()
    st.subheader("👥 Waiting Patients")

    if not waiting.empty:
        for i, (_, row) in enumerate(waiting.head(15).iterrows(), 1):
            c1, c2, c3 = st.columns([2, 2.5, 0.5])
            with c1:
                st.write(f"**#{i}. Patient: {row.get('patient_name') }**")
            with c2:
                st.write(f"⏰ {row['appointment_at']} | 👨‍⚕️ {row.get('doctor_name') or row.get('doctor_id')}")
            with c3:
                if st.button("→", key=f"next_{row['id']}", help="Call next"):
                    success, _ = update_appointment_status(row["id"], "in-progress")
                    if success:
                        st.success("Called!")
                        st.cache_data.clear()
                        st.rerun()
    else:
        st.success("No one waiting!")

    st.divider()

    st.subheader("🏥 Currently Being Served")
    if not serving.empty:
        for _, row in serving.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{row.get('patient_name') or row['patient_id']}** - 👨‍⚕️ {row.get('doctor_name') or row.get('doctor_id')}")
                # st.caption(f"Since {row['checkin_time']}")
            with col2:
                if st.button("✓ Done", key=f"done_{row['id']}"):
                    update_appointment_status(row["id"], "completed")
                    st.cache_data.clear()
                    st.rerun()
    else:
        st.info("No one being served")


@st.cache_data(ttl=15)
def _emergency_appointments_df_cached() -> pd.DataFrame:
    df = _appointments_df_cached("", "All")
    rows = df[df["criticality_level"] == 0]
    rows  = rows[rows["status"] == "scheduled"]
    if rows.empty:
        return pd.DataFrame()
    return rows


@st.cache_data(ttl=60)
def _queue_doctors_picklist_cached() -> List[Dict[str, Any]]:
    docs = get_queue_doctors()
    return docs if docs else []

def _render_emergency_tab() -> None:
    st.subheader("Emergency cases")
    st.caption(
        "Create **emergency** slots (criticality 0): time is stored as **database NOW()**. "
        "Patient must already be registered."
    )
    if st.button("Refresh emergency list", key="refresh_emergency_tab"):
        st.cache_data.clear()
        st.rerun()

    doctors = _queue_doctors_picklist_cached()
    email_labels = {d["user_email"]: f"{d['full_name']} — {d['specialty']}" for d in doctors}
    doctor_emails = [d["user_email"] for d in doctors]

    with st.expander("Create emergency appointment", expanded=True):
        with st.form("form_emergency_quick", clear_on_submit=True):
            eq_patient = st.text_input(
                "Patient email *",
                key="emq_patient",
                help="Must match `patients.user_email`.",
            )
            eq_reason = st.text_area("Reason *", key="emq_reason", height=72)
            eq_doc_email = st.text_input(
                "Doctor email(Assigned)",
                key="emq_doc_email",
                help="Leave blank to create the emergency case without assigning a doctor yet.",
            )
            st.write(" ")
            eq_patient_name = st.text_input(
                "Patient name ",
                key="emq_patient_name",
                help="Used for convenience; appointment creation still uses patient email to find the patient record.",
            )
            st.caption("Appointment time is set automatically on the server (SQL `NOW()`).")
            eq_submit = st.form_submit_button("Create emergency appointment")

        if eq_submit:
            if not (eq_patient or "").strip():
                st.warning("Patient email is required.")
            elif not (eq_reason or "").strip():
                st.warning("Reason is required.")
            else:
                dem = (eq_doc_email or "").strip() or None
                pem = (eq_patient_name or "").strip() or None
                if create_emergency_appointment_quick(
                    patient_email= eq_patient.strip(),
                    reason=eq_reason.strip(),
                    doctor_email=dem,
                    patient_name = pem
                ):
                    st.success("Emergency appointment created.")
                    st.cache_data.clear()
                    st.rerun()

    st.divider()
    st.markdown("**Active emergency cases Pending**")

    df = _emergency_appointments_df_cached()

    if not doctors and not df.empty:
        st.warning("No doctors registered yet—assignments below need doctors in the system.")

    if df.empty:
        st.info("No active emergency appointments.")
    else:
        for _, row in df.iterrows():
            aid = row.get("id")
            pid = row.get("patient_id")
            cur_doc = row.get("doctor_id")
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 2, 2])
                with c1:
                    patient_name = row.get("patient_name") or pid
                    st.write(f"**Patient** `{patient_name}`")
                    st.caption(f"Case ID: `{aid}`")
                with c2:
                    st.write(f"⏰ {row.get('appointment_at')}")
                    st.write(
                        f"**{row.get('status')}** · Assigned doctor id: `{cur_doc if pd.notna(cur_doc) and cur_doc else '—'}`"
                    )
                    if row.get("reason"):
                        st.caption(str(row.get("reason"))[:280])
                


@st.cache_data(ttl=15)
def _emergency_appointments_df_cached() -> pd.DataFrame:
    df = _appointments_df_cached("", "All")
    rows = df[df["criticality_level"] == 0]
    rows  = rows[rows["status"] == "scheduled"]
    if rows.empty:
        return pd.DataFrame()
    return rows


@st.cache_data(ttl=60)
def _queue_doctors_picklist_cached() -> List[Dict[str, Any]]:
    docs = get_queue_doctors()
    return docs if docs else []

def page_dashboard():
    """Queue management: Overview, Update Appointments, Live Queue."""
    st_autorefresh(interval=300000, key="datarefresh")

    _apply_queue_page_styles()
    state = get_state_manager()
    if "queue_doctor_email" not in st.session_state:
        st.session_state.queue_doctor_email = state.get("user_email") or ""

    # st.sidebar.text_input(
    #     "Doctor email filter (empty = all doctors)",
    #     key="queue_doctor_email",
    #     help="Restrict queue to one doctor's calendar, or leave blank for all.",
    # )
    # st.sidebar.text_input(
    #     "Doctor email filter (empty = all doctors)",
    #     key="queue_doctor_email",
    #     help="Restrict queue to one doctor's calendar, or leave blank for all.",
    # )
    doctor_email = st.session_state.queue_doctor_email or ""

    st.title("🏥 Hospital Queue Management")
    st.divider()

    tab_overview, tab_update, tab_live, tab_emergency = st.tabs(
        [
            "Overview",
            "Update Appointments",
            "Live Queue",
            "Emergency",
        ]
    )

    with tab_overview:
        _render_overview_tab("")

    with tab_update:
        _render_update_appointments_tab(st.session_state.get("user"), doctor_email)

    with tab_live:
        _render_live_queue_tab(doctor_email)

    with tab_emergency:
        _render_emergency_tab()



def page_appointments(user):
    """Appointments management page (standalone navigation)."""
    _apply_queue_page_styles()
    state = get_state_manager()
    if "queue_doctor_email" not in st.session_state:
        st.session_state.queue_doctor_email = state.get("user_email") or ""
    doctor_email = st.session_state.queue_doctor_email or ""
    st.title("📋 Appointment Management")
    _render_update_appointments_tab(user, doctor_email)


def page_queue_status():
    """Queue status page (standalone navigation)."""
    _apply_queue_page_styles()
    state = get_state_manager()
    if "queue_doctor_email" not in st.session_state:
        st.session_state.queue_doctor_email = state.get("user_email") or ""
    doctor_email = st.session_state.queue_doctor_email or ""
    st.title("⏳ Real-Time Queue Status")
    _render_live_queue_tab(doctor_email)

# ==================== MAIN ====================

def page_login():
    """Standalone demo login placeholder (main app uses streamlit_app auth)."""
    _apply_queue_page_styles()
    st.title("🏥 Hospital Queue (standalone)")
    st.info("Run the full app with `streamlit run streamlit_app.py` from the `frontend` folder for login.")
    if st.button("Continue as demo (logged in)"):
        st.session_state.logged_in = True
        st.session_state.user = {"username": "demo", "role": "admin"}
        st.rerun()


def main():
    """Main app"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if not st.session_state.logged_in:
        page_login()
    else:
        user = st.session_state.user
        
        with st.sidebar:
            st.title("Navigation")
            page = st.radio("Select", [
                "📊 Dashboard",
                "📋 Appointments",
                "⏳ Queue Status"
            ])
        
        if page == "📊 Dashboard":
            page_dashboard()
        elif page == "📋 Appointments":
            page_appointments(user)
        elif page == "⏳ Queue Status":
            page_queue_status()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Hospital Queue Management",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    main()


