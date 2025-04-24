def parse_file_to_slides(uploaded_file):
    content = uploaded_file.getvalue().decode("utf-8")
    slides = content.split("\n\n")
    return [{"title": f"Слайд {i+1}", "content": slide} for i, slide in enumerate(slides)]