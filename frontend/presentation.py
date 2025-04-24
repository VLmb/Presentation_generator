import os
from pptx import Presentation
from pptx.util import Inches
import comtypes.client
import pythoncom
from PIL import Image
import tempfile


def create_presentation(topic, slides_data, background_path):
    prs = Presentation()
    for slide_data in slides_data:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.add_picture(background_path, 0, 0, width=prs.slide_width, height=prs.slide_height)
        title = slide.shapes.title
        title.text = slide_data["title"]
        left = Inches(1)
        top = Inches(1.5)
        width = prs.slide_width - Inches(2)
        height = prs.slide_height - Inches(2)
        text_box = slide.shapes.add_textbox(left, top, width, height)
        text_frame = text_box.text_frame
        text_frame.text = slide_data["content"]
    pptx_path = f"{topic}.pptx"
    prs.save(pptx_path)
    return pptx_path


def convert_to_pdf(pptx_path):
    pdf_path = pptx_path.replace(".pptx", ".pdf")
    try:
        pythoncom.CoInitialize()
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        deck = powerpoint.Presentations.Open(os.path.abspath(pptx_path))
        deck.SaveAs(os.path.abspath(pdf_path), 32)
        deck.Close()
        powerpoint.Quit()
        return pdf_path
    except Exception as e:
        raise Exception(f"Ошибка конвертации: {str(e)}")
    finally:
        pythoncom.CoUninitialize()


def generate_previews(pptx_path, slides_count):
    previews = []
    try:
        pythoncom.CoInitialize()
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        deck = powerpoint.Presentations.Open(os.path.abspath(pptx_path))

        temp_dir = tempfile.mkdtemp()
        for i in range(1, slides_count + 1):
            img_path = os.path.join(temp_dir, f"slide_{i}.jpg")
            deck.Slides(i).Export(img_path, "JPG")
            previews.append(Image.open(img_path))

        deck.Close()
        powerpoint.Quit()
        return previews
    except Exception as e:
        raise Exception(f"Ошибка генерации превью: {str(e)}")
    finally:
        pythoncom.CoUninitialize()