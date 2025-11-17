import os
import shutil
from video import reverse_video_opencv, blend_two_videos, concat_videos_opencv


def process_and_merge_video_pairs(folders, user_id, filename="samples-rgb.mp4", slow_factor=1.1):
    fused_outputs = []

    fragments_dir = os.path.join("static", "fragments", f"user_{user_id}")
    if os.path.exists(fragments_dir):
        shutil.rmtree(fragments_dir)
    os.makedirs(fragments_dir, exist_ok=True)

    for i in range(0, len(folders), 2):
        if i + 1 < len(folders):
            folder1 = folders[i]
            folder2 = folders[i + 1]
            video1 = os.path.join(folder1, filename)
            video2 = os.path.join(folder2, filename)

            reversed_video2 = os.path.join(fragments_dir, f"temp_reversed_{i // 2}.mp4")
            fused_output = os.path.join(fragments_dir, f"fused_{i // 2 + 1}.mp4")

            reverse_video_opencv(video2, reversed_video2, slow_factor)
            blend_two_videos(video1, reversed_video2, fused_output, slow_factor)

            if os.path.exists(reversed_video2):
                os.remove(reversed_video2)

            fused_outputs.append(fused_output)
        else:
            folder = folders[i]
            video = os.path.join(folder, filename)
            keep_copy = os.path.join(fragments_dir, f"fused_{i // 2 + 1}.mp4")
            shutil.copy(video, keep_copy)
            fused_outputs.append(keep_copy)

    print("Videos to concatenate:", fused_outputs)

    output_dir = os.path.join("static", "final_output", f"user_{user_id}")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "final_output.mp4")
    concat_videos_opencv(fused_outputs, output_path, slow_factor)
