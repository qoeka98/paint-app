

import streamlit as st
from eda import run_eda
from home import run_home
from ml import run_ml

# 🔹 **사이드바 메뉴 추가**
menu_option = st.sidebar.radio("메뉴 선택", ["🏠 홈", "🎮 게임",'앱개발과정'])

if menu_option == "🏠 홈":
    run_home()

elif menu_option == "🎮 게임":
    run_eda()  

elif menu_option == '앱개발과정':
    run_ml()