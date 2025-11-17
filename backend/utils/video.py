import cv2
import os
import shutil
import threading
from seva_renderer import SevaRenderer, ABORT_EVENTS
import torch

def generate_video_from_image(image_path: str, user_id: str, preset_traj: str):
    renderer = SevaRenderer()
    preprocessed_data, _, _ = renderer.preprocess(image_path)

    session_hash = "test-session"
    seed = 23
    chunk_strategy = "nearest"
    cfg = 4.0
    num_frames = 120
    zoom_factor = None
    camera_scale = 2

    ABORT_EVENTS[session_hash] = threading.Event()

    gen = renderer.render(
        preprocessed=preprocessed_data,
        session_hash=session_hash,
        seed=seed,
        chunk_strategy=chunk_strategy,
        cfg=cfg,
        preset_traj=preset_traj,
        num_frames=num_frames,
        zoom_factor=zoom_factor,
        camera_scale=camera_scale,
        user_id=user_id
    )

    for output in gen:
        print("Render step output:", output)


def reverse_video_opencv(input_path, output_path, slow_factor=1):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Could not open {input_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) / slow_factor
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frames = []
    for _ in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    frames.reverse()

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    for frame in frames:
        out.write(frame)
    out.release()

    print(f"Reversed video saved to: {output_path}")


def blend_two_videos(video1_path, video2_path, output_path='blended_video.mp4', slow_factor=1):
    cap1 = cv2.VideoCapture(video1_path)
    cap2 = cv2.VideoCapture(video2_path)

    fps1 = cap1.get(cv2.CAP_PROP_FPS) / slow_factor
    fps2 = cap2.get(cv2.CAP_PROP_FPS) / slow_factor

    # use the minimum fps to avoid sync issues
    fps = min(fps1, fps2)

    width1 = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    height1 = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width2 = int(cap2.get(cv2.CAP_PROP_FRAME_WIDTH))
    height2 = int(cap2.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # use max dimensions to avoid cropping
    width = max(width1, width2)
    height = max(height1, height2)

    frame_count1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))

    transition_duration_frames = int(fps)

    # frames to write fully from video1 before transition
    clip1_end_frame = frame_count1 - transition_duration_frames
    if clip1_end_frame < 0:
        clip1_end_frame = 0

    # frames to skip at start of video2 (overlap transition frames)
    clip2_start_frame = transition_duration_frames

    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    def blend_frames(f1, f2, alpha):
        return cv2.addWeighted(f1, 1 - alpha, f2, alpha, 0)

    current_frame = 0
    # write all frames of video1 before transition
    while current_frame < clip1_end_frame:
        ret1, frame1 = cap1.read()
        if not ret1:
            break
        # resizing
        if frame1.shape[1] != width or frame1.shape[0] != height:
            frame1 = cv2.resize(frame1, (width, height))
        out.write(frame1)
        current_frame += 1

    # read frames for blending
    frames1 = []
    for _ in range(transition_duration_frames):
        ret1, frame1 = cap1.read()
        if not ret1:
            frame1 = None
        else:
            if frame1.shape[1] != width or frame1.shape[0] != height:
                frame1 = cv2.resize(frame1, (width, height))
        frames1.append(frame1)

    frames2 = []
    # skip initial frames of video2 to start blending after the overlap
    for _ in range(clip2_start_frame):
        ret2, _ = cap2.read()
        if not ret2:
            break

    for _ in range(transition_duration_frames):
        ret2, frame2 = cap2.read()
        if not ret2:
            frame2 = None
        else:
            if frame2.shape[1] != width or frame2.shape[0] != height:
                frame2 = cv2.resize(frame2, (width, height))
        frames2.append(frame2)

    # blend transition frames
    for t in range(transition_duration_frames):
        f1 = frames1[t]
        f2 = frames2[t]
        if f1 is None and f2 is None:
            break
        elif f1 is None:
            out.write(f2)
        elif f2 is None:
            out.write(f1)
        else:
            alpha = t / transition_duration_frames
            blended = blend_frames(f1, f2, alpha)
            out.write(blended)

    # write remaining frames from video2 after transition
    while True:
        ret2, frame2 = cap2.read()
        if not ret2:
            break
        if frame2.shape[1] != width or frame2.shape[0] != height:
            frame2 = cv2.resize(frame2, (width, height))
        out.write(frame2)

    cap1.release()
    cap2.release()
    out.release()
    print(f"Blended video saved as: {output_path}")


def concat_videos_opencv(video_paths, output_path, slow_factor=1.0):
    if not video_paths:
        print("No videos to concatenate.")
        return

    # open videos
    caps = [cv2.VideoCapture(v) for v in video_paths]

    if any(not cap.isOpened() for cap in caps):
        print("Error opening one of the video files.")
        for cap in caps:
            cap.release()
        return

    # get properties from first video
    fps = caps[0].get(cv2.CAP_PROP_FPS) / slow_factor
    width = int(caps[0].get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(caps[0].get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    for cap in caps:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # resize
            if (frame.shape[1], frame.shape[0]) != (width, height):
                frame = cv2.resize(frame, (width, height))
            out.write(frame)
        cap.release()

    out.release()
    print(f"Concatenated video saved as: {output_path}")


def fuse_and_merge_video_folders(folders, user_id, filename="samples-rgb.mp4", slow_factor=1.1):
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

    def get_sliding_w2cs(
            ref_w2c: torch.Tensor,
            direction: str,
            num_frames: int,
            device=None,
    ) -> torch.Tensor:
        """
        Generate poses by sliding the camera left or right in its local coordinate frame,
        keeping orientation fixed (like a dolly move).
        Used in Stable-Virtual-Camera, "geometry.py".
        """
        distance = 20
        if device is None:
            device = ref_w2c.device

        # convert to camera-to-world (extrinsic) for manipulation
        ref_c2w = torch.linalg.inv(ref_w2c)
        ref_position = ref_c2w[:3, 3].clone()
        right_vector = ref_c2w[:3, 0]
        left_vector = -ref_c2w[:3, 0]

        if direction == "right":
            move_vec = left_vector
        elif direction == "left":
            move_vec = right_vector
        else:
            raise ValueError(f"Unknown direction '{direction}', must be 'left' or 'right'")

        positions = [
            ref_position + move_vec * (distance * t)
            for t in torch.linspace(0, 1, num_frames, device=device)
        ]

        # The orientation stays the same as original
        R = ref_c2w[:3, :3]
        poses = []
        for pos in positions:
            c2w = torch.eye(4, device=device)
            c2w[:3, :3] = R
            c2w[:3, 3] = pos
            w2c = torch.linalg.inv(c2w)
            poses.append(w2c)
        return torch.stack(poses, dim=0)