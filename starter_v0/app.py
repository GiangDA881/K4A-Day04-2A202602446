import streamlit as st
import json

def mock_run_agent(user_input, history):
    # Đây chỉ là hàm giả lập để bạn thấy cách UI hoạt động
    # Bạn sẽ thay hàm này bằng luồng gọi LLM thật của nhóm
    return [
        {"role": "assistant", "content": None, "tool_calls": [{"name": "check_service_status", "arguments": '{"service": "VPN"}'}]},
        {"role": "tool", "tool_name": "check_service_status", "content": '{"status": "ONLINE", "message": "VPN is running normally."}'},
        {"role": "assistant", "content": "Hệ thống ghi nhận dịch vụ VPN hiện đang hoạt động bình thường (ONLINE). Bạn có cần kiểm tra thêm gì không?"}
    ]

# Cấu hình trang
st.set_page_config(page_title="IT Helpdesk Agent", page_icon="🛠️", layout="centered")
st.title("🛠️ Cổng Hỗ Trợ IT Nội Bộ")

# ==========================================
# BƯỚC 2: QUẢN LÝ SESSION STATE
# ==========================================
# Khởi tạo danh sách tin nhắn nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Chào bạn, tôi là IT Helpdesk Agent. Tôi có thể giúp gì cho bạn hôm nay?"}
    ]

# ==========================================
# BƯỚC 3: THIẾT KẾ HIỂN THỊ TOOL CALLS VÀ LỊCH SỬ CHAT
# ==========================================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
            
    elif msg["role"] == "assistant":
        # Nếu assistant trả về text bình thường
        if msg.get("content"):
            with st.chat_message("assistant"):
                st.write(msg["content"])
                
        # Nếu assistant gọi tool
        if msg.get("tool_calls"):
            with st.chat_message("assistant", avatar="⚙️"):
                for tool in msg["tool_calls"]:
                    with st.expander(f"🛠️ Agent đang gọi: `{tool['name']}`"):
                        st.json(json.loads(tool["arguments"]))
                        
    elif msg["role"] == "tool":
        # Hiển thị kết quả trả về từ tool ẩn trong expander
        with st.chat_message("tool", avatar="🔧"):
            with st.expander(f"✅ Kết quả từ `{msg.get('tool_name', 'tool')}`"):
                try:
                    # Cố gắng format JSON cho đẹp
                    st.json(json.loads(msg["content"]))
                except:
                    # Nếu không phải JSON thì in text bình thường
                    st.text(msg["content"])

# ==========================================
# BƯỚC 4: TÍCH HỢP LOGIC XỬ LÝ (INPUT TỪ USER)
# ==========================================
if user_input := st.chat_input("Nhập yêu cầu hỗ trợ (VD: Kiểm tra trạng thái VPN)..."):
    # 1. Hiển thị ngay câu hỏi của user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. Gọi Agent xử lý
    with st.spinner("Agent đang xử lý..."):
        # THAY MOCK BẰNG HÀM THẬT CỦA BẠN TẠI ĐÂY
        # Lấy lịch sử chat hiện tại để truyền cho agent (nếu cần context)
        chat_history = st.session_state.messages[:-1] 
        
        # Gọi agent
        new_messages = mock_run_agent(user_input, chat_history)
        
        # 3. Lưu kết quả vào Session State và force reload để render lại màn hình
        for new_msg in new_messages:
            st.session_state.messages.append(new_msg)
            
        st.rerun()