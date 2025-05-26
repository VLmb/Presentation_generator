import os


BACKGROUNDS = {
    # "Синий градиент": "backgrounds/blue_gradient.jpg",
    # "Тёмный узор": "backgrounds/dark_pattern.jpg",
    "Светлый мрамор": "backgrounds/light_marble.jpg",
    "Мифи": "backgrounds/mephi.jpg",
    "Мифи синий": "backgrounds/mephi1.jpg",
}

def init_environment() -> None:
    os.makedirs("backgrounds", exist_ok=True)