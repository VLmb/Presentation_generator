import os


BACKGROUNDS = {
    "Синий градиент": "backgrounds/blue_gradient.jpg",
    "Тёмный узор": "backgrounds/dark_pattern.jpg",
    "Светлый мрамор": "backgrounds/light_marble.jpg"
}

def init_environment():
    os.makedirs("backgrounds", exist_ok=True)
    return True