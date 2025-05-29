import os


BACKGROUNDS = {
    # "Синий градиент": "backgrounds/blue_gradient.jpg",
    # "Тёмный узор": "backgrounds/dark_pattern.jpg",
    # "Светлый мрамор": "backgrounds/light_marble.jpg",
    "МИФИческий белый": "backgrounds/mephi.jpg",
    "МИФИческий синий": "backgrounds/mephi1.jpg",
}

def init_environment() -> None:
    os.makedirs("backgrounds", exist_ok=True)