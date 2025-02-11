import streamlit as st
from eda import run_eda
from home import run_home
from ml import run_ml

# 🔹 **사이드바 메뉴 추가**
st.sidebar.title("📌 메뉴 선택")
menu_option = st.sidebar.radio("메뉴를 선택하세요", ["🏠 홈", "🎮 게임", "📚 앱 개발 과정"])

if menu_option == "🏠 홈":
    run_home()

elif menu_option == "🎮 게임":
    run_eda()

elif menu_option == "📚 앱 개발 과정":
    run_ml()
