import os
import io
from typing import List
import docx
import PyPDF2
import requests
import streamlit as st

from presentation import create_presentation, convert_to_pdf, generate_previews
from file_processor import parse_file_to_slides
from config import BACKGROUNDS, init_environment


def extract_text_from_file(uploaded_file) -> str:
        """
        Извлекает текст из загруженного файла (txt, pdf, docx).
        Returns:
            str: Извлечённый текст.
        """
        filename = uploaded_file.name.lower()
        if filename.endswith('.txt'):
            return uploaded_file.getvalue().decode("utf-8")
        elif filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            return text
        elif filename.endswith('.docx'):
            doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        else:
            return ""

init_environment()

st.title("📊 Генератор презентаций")

mode = st.radio("Режим работы:", ["Обычный генератор", "Генератор по файлу"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    topic = st.text_input("Название презентации", "Моя презентация")
with col2:
    selected_bg = st.selectbox("Фон презентации", list(BACKGROUNDS.keys()))
bg_path = BACKGROUNDS[selected_bg]

slides_count = st.number_input("Количество слайдов", 1, 50, 3)

if mode == "Генератор по файлу":
    uploaded_file = st.file_uploader("Загрузите файл (txt, pdf, docx)", type=["txt", "pdf", "docx"])
    if uploaded_file:
        file_text = extract_text_from_file(uploaded_file)
        if file_text.strip():
            st.success(f"Файл успешно загружен")
        else:
            st.warning(f"Вы загрузили пустой файл")


if st.button("Создать презентацию", type="primary"):
    with st.spinner("Идёт создание презентации..."):
        slides_data = {
            "Presentation_title": topic,
            "Slide_count": slides_count,
        }


        if mode == "Генератор по файлу":
            slides_data["Description"] = file_text.strip()
            response = requests.post(
                "http://localhost:5000/api_backend/gen_presentation_by_text",
                json=slides_data
            )
            slides_data['Slides'] = response.json().get('Slides', [])
            
        else:
            slides_data['Slides'] = [{
                "Slide_title": "",
                "Slide_content": ""
            } for _ in range(slides_count)]
            response = requests.post(
                "http://localhost:5000/api_backend/gen_presentation_by_title",
                json=slides_data
            )
            slides_data['Slides'] = response.json().get('Slides', [])

        # st.success(f"Кол-во слайдов: {len(slides_data['Slides'])}")
        # st.success(f"Слайды: {slides_data['Slides']}")
        # slides_data = {
        #     "Presentation_title": "Французская революция",
        #     "Slide_count": 3,
        #     "Slides": [
        #         {
        #         "Slide_title": "Что вообще произошло? Вводный слайд",
        #         "Slide_content": "Общее представление о революции: когда, где и почему она началась. Франция конца XVIII века — котёл, готовый взорваться."
        #         },
        #         {
        #         "Slide_title": "Франция до революции: пахнет жареным",
        #         "Slide_content": "Кризис монархии, госдолг, бедность и беспредел — классическая завязка для грандиозного бунта. Людовик XVI не справляется."
        #         },
        #         {
        #         "Slide_title": "Три сословия и ноль справедливости",
        #         "Slide_content": "Разделение общества на духовенство, знать и всех остальных. Привилегии первых двух и страдания третьего."
        #         }
        #     ]
        #     }

    
        pptx_path = create_presentation(topic, slides_data, bg_path)
        pdf_path = convert_to_pdf(pptx_path)
        previews = generate_previews(pptx_path, len(slides_data)+1)

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