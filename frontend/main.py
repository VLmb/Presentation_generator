import streamlit as st
from .presentation import create_presentation, convert_to_pdf, generate_previews
from .file_processor import parse_file_to_slides
from .config import BACKGROUNDS, init_environment
import os

init_environment()

st.title("📊 Генератор презентаций")
mode = st.radio("Режим работы:", ["Обычный генератор", "Генератор по файлу"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    topic = st.text_input("Название презентации", "Моя презентация")
with col2:
    selected_bg = st.selectbox("Фон презентации", list(BACKGROUNDS.keys()))
bg_path = BACKGROUNDS[selected_bg]

if mode == "Обычный генератор":
    slides_count = st.number_input("Количество слайдов", 1, 50, 3)
    slides_data = [{"title": f"Слайд {i + 1}", "content": ""} for i in range(slides_count)]
    for i, slide in enumerate(slides_data):
        with st.expander(f"Слайд {i + 1}"):
            slide["title"] = st.text_input("Заголовок", slide["title"], key=f"title_{i}")
            slide["content"] = st.text_area("Содержание", slide["content"], key=f"content_{i}")
else:
    uploaded_file = st.file_uploader("Загрузите текстовый файл", type=["txt"])
    if uploaded_file:
        slides_data = parse_file_to_slides(uploaded_file)
        st.success(f"Загружено {len(slides_data)} слайдов")
    else:
        slides_data = []

if st.button("Создать презентацию", type="primary") and slides_data:
    with st.spinner("Идёт создание презентации..."):
        pptx_path = create_presentation(topic, slides_data, bg_path)
        pdf_path = convert_to_pdf(pptx_path)
        previews = generate_previews(pptx_path, len(slides_data))

    st.success("Готово!")

    if previews:
        st.subheader("Превью слайдов")
        cols = st.columns(3)
        for i, img in enumerate(previews):
            cols[i % 3].image(img, caption=f"Слайд {i + 1}", use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        with open(pptx_path, "rb") as f:
            st.download_button(
                "📥 Скачать PPTX",
                f.read(),
                file_name=os.path.basename(pptx_path),
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
    with col2:
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "📥 Скачать PDF",
                    f.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf"
                )