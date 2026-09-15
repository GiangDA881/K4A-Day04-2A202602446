import json
import os
import sys
from pathlib import Path
import streamlit as st

# Thiết lập đường dẫn root
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version
from ticket_session import TicketSession
from chat import run_model_tool_loop, trim_history

# Tải cấu hình môi trường
load_lab_env(ROOT)

ARTIFACTS_DIR = ROOT / "artifacts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Northstar IT Helpdesk Agent",
    page_icon="🛠️",
    layout="wide",
)

@st.cache_resource
def init_agent_backend():
    """Khởi tạo cấu hình và provider dùng chung cho session."""
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tool_declarations = load_tool_declarations(TOOLS_PATH)
    openai_tools = to_openai_tools(tool_declarations)

    provider_name = "openai" if os.environ.get("OPENAI_API_KEY") else "gemini"
    provider = make_provider(provider_name)
    model_name = os.environ.get("LLM_MODEL") or getattr(provider, "default_model", None)

    artifact_version = build_artifact_version("v5", SYSTEM_PROMPT_PATH, TOOLS_PATH)

    return {
        "system_prompt": system_prompt,
        "openai_tools": openai_tools,
        "provider": provider,
        "provider_name": provider_name,
        "model_name": model_name,
        "artifact_version": artifact_version,
    }

backend = init_agent_backend()
av = backend["artifact_version"]

# ==========================================
# QUẢN LÝ SESSION STATE
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Tôi là Northstar IT Helpdesk Agent. Tôi có thể hỗ trợ chẩn đoán thiết bị, kiểm tra dịch vụ hạ tầng, tra cứu chính sách/KB hoặc tạo ticket hỗ trợ. Bạn cần hỗ trợ gì hôm nay?"}
    ]

if "history" not in st.session_state:
    st.session_state.history = []

if "ticket_session" not in st.session_state:
    st.session_state.ticket_session = TicketSession()

# ==========================================
# SIDEBAR — THÔNG TIN PHIÊN BẢN & AUDIT
# ==========================================
with st.sidebar:
    st.header("🛠️ Hệ Thống & Kiểm Tra")
    st.success("🟢 Kết nối Agent: LLM Thật (Live Loop)")

    st.markdown("### 📌 Phiên bản Artifacts")
    st.code(f"Version: {av.artifact_version}\nPrompt Hash: {av.prompt_hash[:12]}...\nTools Hash:  {av.tools_hash[:12]}...", language="text")

    st.markdown("### 🤖 Cấu Hình Model")
    st.write(f"**Provider:** `{backend['provider_name']}`")
    st.write(f"**Model:** `{backend['model_name']}`")

    st.markdown("### 📋 Công cụ tích hợp (10 tools)")
    st.caption("check_service_status, inspect_device, search_kb, lookup_user, format_incident_report, policy, create_ticket, search_device_info, clarify, lookup_ticket_status (bonus)")

    st.divider()
    if st.button("🔄 Làm mới phiên hội thoại", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Phiên làm việc đã được đặt lại. Tôi có thể giúp gì cho bạn?"}
        ]
        st.session_state.history = []
        st.session_state.ticket_session = TicketSession()
        st.rerun()

    st.markdown("### 💡 Câu hỏi mẫu (Demo)")
    quick_prompts = [
        "Kiểm tra VPN công ty và chẩn đoán kết nối máy LT-204",
        "Môi trường test của dịch vụ Email đang thế nào?",
        "Tôi xác nhận tạo ticket: VPN lỗi AUTH_TIMEOUT trên LT-204, priority high.",
        "Ticket LAB-DE000001 của tôi hiện có trạng thái gì trong hệ thống?",
    ]
    for q in quick_prompts:
        if st.button(f"👉 {q[:35]}...", key=q, help=q, use_container_width=True):
            st.session_state["pending_input"] = q
            st.rerun()

# ==========================================
# GIAO DIỆN CHAT CHÍNH
# ==========================================
st.title("🛠️ Northstar IT Helpdesk Portal")
st.caption(f"Hệ thống hỗ trợ kỹ thuật nội bộ thông minh — Phiên bản: `{av.artifact_version}`")

for msg in st.session_state.messages:
    role = msg["role"]
    if role == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])

    elif role == "assistant":
        if msg.get("tool_calls"):
            with st.chat_message("assistant", avatar="⚙️"):
                for tool in msg["tool_calls"]:
                    with st.expander(f"🛠️ Agent đang gọi: `{tool['name']}`", expanded=True):
                        args = tool.get("arguments") or tool.get("args")
                        if isinstance(args, str):
                            try:
                                args = json.loads(args)
                            except Exception:
                                pass
                        st.json(args)

        if msg.get("content"):
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    elif role == "tool":
        with st.chat_message("tool", avatar="🔧"):
            with st.expander(f"✅ Kết quả từ `{msg.get('tool_name', 'tool')}`", expanded=False):
                content = msg.get("content")
                if isinstance(content, str):
                    try:
                        content = json.loads(content)
                    except Exception:
                        pass
                if isinstance(content, (dict, list)):
                    st.json(content)
                else:
                    st.text(str(content))

# ==========================================
# XỬ LÝ INPUT TỪ NGƯỜI DÙNG
# ==========================================
user_input = st.chat_input("Nhập yêu cầu hỗ trợ (VD: Kiểm tra VPN và chẩn đoán máy LT-204)...")
if not user_input and "pending_input" in st.session_state:
    user_input = st.session_state.pop("pending_input")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    system_prompt = backend["system_prompt"]
    turn_messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, 5),
        {"role": "user", "content": user_input},
    ]

    with st.spinner("Agent đang xử lý yêu cầu và điều phối tools..."):
        try:
            result = run_model_tool_loop(
                provider=backend["provider"],
                messages=turn_messages,
                tools=backend["openai_tools"],
                model=backend["model_name"],
                max_tool_rounds=4,
                ticket_session=st.session_state.ticket_session,
            )

            for round_rec in result.get("rounds", []):
                calls = round_rec.get("tool_calls", [])
                if calls:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{"name": c["name"], "arguments": c.get("args", {})} for c in calls]
                    })

                for event in round_rec.get("tool_results", []):
                    st.session_state.messages.append({
                        "role": "tool",
                        "tool_name": event.get("tool", "tool"),
                        "content": event.get("result", {})
                    })

            assistant_text = result.get("assistant_text") or "Đã xử lý xong yêu cầu của bạn."
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_text
            })

            st.session_state.history.append({"role": "user", "content": user_input})
            st.session_state.history.append({"role": "assistant", "content": assistant_text})

        except Exception as exc:
            st.error(f"Lỗi khi thực thi Agent: {type(exc).__name__} - {str(exc)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"⚠️ Rất tiếc, đã có lỗi kết nối hoặc xử lý xảy ra: {str(exc)}"
            })

    st.rerun()