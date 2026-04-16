import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime
from PIL import Image
import os
import uuid
import base64

# -------------------------- 全局初始化 --------------------------
st.set_page_config(
    page_title="AI笔记大师",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化 Session
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_note" not in st.session_state:
    st.session_state.current_note = None
if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""
if "avatar_updated" not in st.session_state:
    st.session_state.avatar_updated = False
if "clear_triggered" not in st.session_state:
    st.session_state.clear_triggered = False


# -------------------------- 主题样式（只删除顶部白条） --------------------------
def apply_theme():
    st.markdown("""
    <style>
    /* 精准删除你红色框里的顶部白条 */
    #MainMenu {visibility: hidden;}
    header {display: none !important;}

    /* 以下是原有正常样式，不动 */
    .stSidebar { 
        background-color: #f8f9fa !important; 
        border-right: 1px solid #000 !important;
    }
    .stCard {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin: 12px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    .stButton>button {
        background-color: #0d6efd;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
    }
    hr {
        border: none;
        height: 1px;
        background-color: #000 !important;
        margin: 16px 0;
    }
    </style>
    """, unsafe_allow_html=True)
# -------------------------- 导入配套模块 --------------------------
from data_storage import user_manager, note_manager
from api_client import (
    ai_summarize_note,
    ai_extract_keywords,
    ai_rewrite_note,
    ai_generate_mindmap,
    ai_chat_with_notes
)


# -------------------------- 头像工具函数 --------------------------
def save_avatar(user_id, uploaded_file):
    """保存用户头像到本地"""
    avatar_dir = "avatars"
    os.makedirs(avatar_dir, exist_ok=True)
    file_path = os.path.join(avatar_dir, f"{user_id}_avatar.png")
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    user_manager.update_avatar(user_id, file_path)
    st.session_state.avatar_updated = True


def get_avatar_path(user_id):
    """获取用户头像路径"""
    avatar_path = f"avatars/{user_id}_avatar.png"
    if os.path.exists(avatar_path):
        return avatar_path
    return None


# -------------------------- 登录注册页面（新增头像） --------------------------
def login_register_page():
    # 加载Logo
    if os.path.exists("logo.png"):
        logo = Image.open("logo.png")
        st.image(logo, width=100)
        st.markdown("""
            <div style="text-align: center; margin: 40px 0;">
                <h1 style="font-size: 5rem; font-weight: 1000; color: #212529; margin: 0 0 20px 0; letter-spacing: 2px;">AI笔记管理系统</h1>
                <h2 style="font-size: 2.2rem; font-weight: 600; color: #495057; margin: 0; opacity: 0.9;">智能 · 高效 · 一站式笔记管理</h2>
            </div>
        """, unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["登 录", "注 册"])

    with tab1:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("用户登录")
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")

        if st.button("登录"):
            user = user_manager.login_user(username, password)
            if user:
                st.session_state.current_user = user
                st.success("登录成功")
                st.rerun()
            else:
                st.error("用户名或密码错误")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        st.subheader("用户注册")
        new_username = st.text_input("设置用户名")
        new_password = st.text_input("设置密码", type="password")
        confirm = st.text_input("确认密码", type="password")

        if st.button("注册"):
            if new_password != confirm:
                st.error("两次密码不一致")
            elif len(new_password) < 6:
                st.error("密码至少6位")
            else:
                ok = user_manager.register_user(new_username, new_password)
                if ok:
                    st.success("注册成功！请登录")
                else:
                    st.error("用户名已存在")
        st.markdown('</div>', unsafe_allow_html=True)


# -------------------------- 主应用 --------------------------
def main_app_page():
    user = st.session_state.current_user
    if not user:
        st.rerun()

    with st.sidebar:
        # 头像展示
        avatar_path = get_avatar_path(user["user_id"])
        if avatar_path:
            st.image(avatar_path, width=80, caption="我的头像", use_column_width=False)
        else:
            st.markdown('<div class="avatar-container">', unsafe_allow_html=True)
            st.markdown(
                '<div class="avatar-img" style="background-color:#0d6efd; color:white; line-height:80px;">无头像</div>',
                unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.subheader(f"你好，{user['username']}")
        st.caption(f"上次登录：{user['last_login']}")
        st.markdown("<hr>", unsafe_allow_html=True)  # 黑色细线分割

        # 导航菜单
        selected = option_menu(
            menu_title="功能导航",
            options=["笔记首页", "笔记创作", "AI工具", "个人中心"],
            icons=["house", "pencil", "robot", "person"],
            default_index=0
        )

        st.markdown("<hr>", unsafe_allow_html=True)
        # 退出登录
        if st.button("退出登录"):
            st.session_state.current_user = None
            st.session_state.current_note = None
            st.rerun()

    # 页面路由
    if selected == "笔记首页":
        show_note_home()
    elif selected == "笔记创作":
        show_note_editor()
    elif selected == "AI工具":
        show_ai_tools()
    elif selected == "个人中心":
        show_user_center()


# -------------------------- 笔记首页（优化查看功能） --------------------------
def show_note_home():
    st.title("📋 我的笔记")
    user_id = st.session_state.current_user["user_id"]
    notes = note_manager.get_user_notes(user_id)

    if not notes:
        st.info("暂无笔记，快去创作吧！")
        return

    # 笔记列表（卡片式展示，优化查看）
    for note in notes:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        col1, col2 = st.columns([4, 1])

        with col1:
            st.subheader(note["title"])
            st.caption(f"分类：{note['category']} | 标签：{', '.join(note['tags'])} | 更新时间：{note['update_time']}")
            # 内容预览
            preview = note["content"][:150] + "..." if len(note["content"]) > 150 else note["content"]
            st.markdown(preview)

        with col2:
            # 查看/编辑按钮 → 点击直接跳转到 笔记创作
            if st.button("✏查看/编辑", key=f"edit_{note['note_id']}"):
                st.session_state.current_note = note
                # 强制切换菜单到 笔记创作
                st.session_state["option_menu_key"] = "笔记创作"
                st.rerun()
            # 删除按钮
            if st.button("删除", key=f"del_{note['note_id']}", type="secondary"):
                note_manager.delete_note(note["note_id"], user_id)
                st.success("删除成功")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)  # 黑色细线分割


# -------------------------- 笔记创作/编辑页（优化添加功能） --------------------------
def show_note_editor():
    st.title("✏️ 笔记创作")
    user_id = st.session_state.current_user["user_id"]

    # 清空触发 → 立即清空
    if st.session_state.clear_triggered:
        st.session_state.current_note = None
        st.session_state.clear_triggered = False

    current_note = st.session_state.current_note

    # 初始化表单数据
    if current_note:
        title = current_note["title"]
        content = current_note["content"]
        category = current_note["category"]
        tags = ", ".join(current_note["tags"])
        note_id = current_note["note_id"]
    else:
        title = ""
        content = ""
        category = "未分类"
        tags = ""
        note_id = None

    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    # 标题+分类+标签
    col1, col2 = st.columns(2)
    with col1:
        new_title = st.text_input("笔记标题", value=title, key="note_title")
    with col2:
        categories = note_manager.get_all_categories(user_id)
        categories = list(set(categories + [category]))
        category_option = st.selectbox("笔记分类", categories,
                                       index=categories.index(category) if category in categories else 0)
        new_category = st.text_input("自定义分类", value=category_option, key="note_category")

    new_tags = st.text_input("笔记标签（逗号分隔）", value=tags, key="note_tags")
    tag_list = [t.strip() for t in new_tags.split(",") if t.strip()]

    # Markdown编辑+实时预览
    st.subheader("📝 笔记内容（支持Markdown）")
    col_edit, col_preview = st.columns(2)

    with col_edit:
        new_content = st.text_area("编辑区", value=content, height=400, key="note_content")
    with col_preview:
        st.subheader("实时预览")
        st.markdown(new_content)

    # 保存按钮
    col_save, col_clear = st.columns(2)
    with col_save:
        if st.button("💾 保存笔记", key="save_note_btn", use_container_width=True):
            if not new_title:
                st.error("请输入笔记标题")
                return
            if not new_content:
                st.error("请输入笔记内容")
                return

            if note_id:
                # 更新笔记
                success = note_manager.update_note(
                    note_id, user_id, new_title, new_content, new_category, tag_list
                )
                if success:
                    st.success("笔记更新成功！")
                    st.session_state.current_note = None
                    st.rerun()
                else:
                    st.error("笔记更新失败")
            else:
                # 新增笔记
                note_manager.add_note(
                    user_id, new_title, new_content, new_category, tag_list
                )
                st.success("笔记创建成功！")
                st.session_state.current_note = None
                st.rerun()

    with col_clear:
        if st.button("🧹 清空内容", key="clear_note_btn", use_container_width=True):
            # 立即清空，不刷新页面
            st.session_state.clear_triggered = True
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# -------------------------- AI工具页（新增插入/替换到笔记功能） --------------------------
def show_ai_tools():
    st.title("🤖 AI智能工具")
    user_id = st.session_state.current_user["user_id"]
    notes = note_manager.get_user_notes(user_id)

    if not notes:
        st.warning("请先创建笔记再使用AI工具")
        return

    # 选择笔记
    note_map = {f"{n['title']} (ID:{n['note_id'][:8]})": n for n in notes}
    selected_note_str = st.selectbox("选择要处理的笔记", list(note_map.keys()))
    selected_note = note_map[selected_note_str]

    # 同步当前笔记到session（用于插入内容）
    st.session_state.current_note = selected_note

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "总 结", "关键词", "创作", " 思维导图", " AI问答"
    ])

    # 1. 笔记总结
    with tab1:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        if st.button("生成总结", key="sum_btn"):
            with st.spinner("AI正在总结中..."):
                result = ai_summarize_note(selected_note["content"])
                if "❌" in result:
                    st.error(result)
                else:
                    st.session_state.ai_result = result
                    st.markdown("### 总结结果")
                    st.markdown(result)
        # 插入/替换按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📌 插入到笔记末尾", key="insert_sum"):
                if st.session_state.ai_result and "❌" not in st.session_state.ai_result:
                    new_content = f"{selected_note['content']}\n\n---\n### AI总结\n{st.session_state.ai_result}"
                    note_manager.update_note(
                        selected_note["note_id"], user_id, selected_note["title"],
                        new_content, selected_note["category"], selected_note["tags"]
                    )
                    st.success("已插入到笔记！")
                    st.rerun()
        with col2:
            if st.button(" 替换笔记内容", key="replace_sum"):
                if st.session_state.ai_result and "❌" not in st.session_state.ai_result:
                    note_manager.update_note(
                        selected_note["note_id"], user_id, selected_note["title"],
                        st.session_state.ai_result, selected_note["category"], selected_note["tags"]
                    )
                    st.success("已替换笔记内容！")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. 关键词提取
    with tab2:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        if st.button("提取关键词", key="kw_btn"):
            with st.spinner("AI正在提取中..."):
                result = ai_extract_keywords(selected_note["content"])
                if "❌" in result:
                    st.error(result)
                else:
                    st.session_state.ai_result = result
                    st.success(f"关键词：{result}")
        # 插入标签按钮
        if st.button(" 添加到笔记标签", key="add_tag"):
            if st.session_state.ai_result and "❌" not in st.session_state.ai_result:
                new_tags = list(set(selected_note["tags"] + [t.strip() for t in st.session_state.ai_result.split(",")]))
                note_manager.update_note(
                    selected_note["note_id"], user_id, selected_note["title"],
                    selected_note["content"], selected_note["category"], new_tags
                )
                st.success("标签添加成功！")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 3. 辅助创作
    with tab3:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        mode = st.selectbox("创作模式", ["续写", "润色", "扩写"])
        if st.button("生成内容", key="rewrite_btn"):
            with st.spinner("AI正在创作中..."):
                result = ai_rewrite_note(selected_note["content"], mode)
                if "❌" in result:
                    st.error(result)
                else:
                    st.session_state.ai_result = result
                    st.markdown("### 创作结果")
                    st.markdown(result)
        # 插入/替换按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button(" 插入到笔记末尾", key="insert_rewrite"):
                if st.session_state.ai_result and "❌" not in st.session_state.ai_result:
                    new_content = f"{selected_note['content']}\n\n---\n### AI{mode}\n{st.session_state.ai_result}"
                    note_manager.update_note(
                        selected_note["note_id"], user_id, selected_note["title"],
                        new_content, selected_note["category"], selected_note["tags"]
                    )
                    st.success("已插入到笔记！")
                    st.rerun()
        with col2:
            if st.button(" 替换笔记内容", key="replace_rewrite"):
                if st.session_state.ai_result and "❌" not in st.session_state.ai_result:
                    note_manager.update_note(
                        selected_note["note_id"], user_id, selected_note["title"],
                        st.session_state.ai_result, selected_note["category"], selected_note["tags"]
                    )
                    st.success("已替换笔记内容！")
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 4. 思维导图
    with tab4:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        if st.button("生成导图结构", key="mindmap_btn"):
            with st.spinner("AI正在生成中..."):
                result = ai_generate_mindmap(selected_note["content"])
                if "❌" in result:
                    st.error(result)
                else:
                    st.session_state.ai_result = result
                    st.markdown("### 思维导图结构（Markdown）")
                    st.code(result, language="markdown")
        # 插入到笔记按钮
        if st.button(" 插入到笔记末尾", key="insert_mindmap"):
            if st.session_state.ai_result and "❌" not in st.session_state.ai_result:
                new_content = f"{selected_note['content']}\n\n---\n### 思维导图\n```markdown\n{st.session_state.ai_result}\n```"
                note_manager.update_note(
                    selected_note["note_id"], user_id, selected_note["title"],
                    new_content, selected_note["category"], selected_note["tags"]
                )
                st.success("已插入到笔记！")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. AI问答
    with tab5:
        st.markdown('<div class="stCard">', unsafe_allow_html=True)
        question = st.text_input("请输入你的问题", key="ai_q")
        if st.button("提问", key="chat_btn"):
            if not question.strip():
                st.error("请输入问题")
                return
            with st.spinner("AI正在思考中..."):
                result = ai_chat_with_notes(selected_note["content"], question)
                if "❌" in result:
                    st.error(result)
                else:
                    st.session_state.ai_result = result
                    st.markdown("### AI回答")
                    st.markdown(result)
        # 插入到笔记按钮
        if st.button(" 插入到笔记末尾", key="insert_chat"):
            if st.session_state.ai_result and "❌" not in st.session_state.ai_result:
                new_content = f"{selected_note['content']}\n\n---\n### Q: {question}\nA: {st.session_state.ai_result}"
                note_manager.update_note(
                    selected_note["note_id"], user_id, selected_note["title"],
                    new_content, selected_note["category"], selected_note["tags"]
                )
                st.success("已插入到笔记！")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# -------------------------- 个人中心（新增头像上传） --------------------------
def show_user_center():
    st.title("👤 个人中心")
    user = st.session_state.current_user
    user_id = user["user_id"]
    # 用户信息卡片
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.subheader("用户信息")
    col1, col2 = st.columns([1, 3])
    with col1:
        avatar_path = get_avatar_path(user_id)
        if avatar_path:
            st.image(avatar_path, width=120)
        else:
            st.markdown(
                '<div class="avatar-img" style="background-color:#0d6efd; color:white; line-height:120px; width:120px; text-align:center;">无头像</div>',
                unsafe_allow_html=True)
    with col2:
        st.write(f"**用户名**：{user['username']}")
        st.write(f"**用户ID**：{user['user_id']}")
        st.write(f"**注册时间**：{user['create_time']}")
        st.write(f"**上次登录**：{user['last_login']}")
    # 头像上传
    st.subheader("上传头像")
    uploaded_file = st.file_uploader("选择头像图片", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        if st.button("保存头像"):
            save_avatar(user_id, uploaded_file)
            st.success("头像保存成功！")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    # 数据统计
    st.markdown('<div class="stCard">', unsafe_allow_html=True)
    st.subheader("数据统计")
    notes = note_manager.get_user_notes(user_id)
    st.write(f"**总笔记数**：{len(notes)}")
    st.write(f"**分类数**：{len(note_manager.get_all_categories(user_id))}")
    st.write(f"**标签数**：{len(note_manager.get_all_tags(user_id))}")
    st.markdown('</div>', unsafe_allow_html=True)
# -------------------------- 入口 --------------------------
if __name__ == "__main__":
    if st.session_state.current_user:
        main_app_page()
    else:
        login_register_page()