import os
import os.path as osp
import datetime
WORK_DIR = "static/generated_videos"
VERSION_DICT = {
    "H": 384,
    "W": 384,
    "T": 21,
    "C": 4,
    "f": 8,
    "options": {},
}


class SevaRenderer():

    def preprocess(self):
        shorter: int = 384

    def render(user_id):
        user_work_dir = osp.join(WORK_DIR, f"user_{user_id}")
        os.makedirs(user_work_dir, exist_ok=True)

        render_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        render_dir = osp.join(user_work_dir, render_name)
        num_steps = 15

