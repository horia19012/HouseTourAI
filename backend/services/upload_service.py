import json
import os
import shutil
import threading
import time

from flask import current_app
from werkzeug.utils import secure_filename

from extensions import socketio
from utils.file_utils import (
    get_latest_folders_with_file, clear_user_workspace
)
from utils.movements import (
    get_movements_for_images_numbered,
    split_and_reverse_moves, extract_number
)
from utils.s3 import (
    upload_final_output_to_s3
)
from utils.sockets import (
    send_message_to_user, send_info_to_user,
    send_image_progress, on_upload_complete,
    check_and_handle_running_uploads
)
from utils.video import (
    fuse_and_merge_video_folders,
    generate_video_from_image
)

user_progress_threads = {}


def handle_upload(request, current_user):
    user_id = request.form.get('user_id')

    if user_id != current_user:
        return {"error": "Unauthorized access"}, 403

    if not user_id:
        return {"error": "user_id is required"}, 400

    app_root = current_app.root_path
    upload_folder = os.path.join(app_root, 'static', 'uploads')
    generated_videos_folder = os.path.join(app_root, 'static', 'generated_videos')

    queue_check = check_and_handle_running_uploads(socketio, user_id=user_id)
    if queue_check:
        return queue_check[0], queue_check[1]

    try:
        files = request.files.getlist('images')
        relations_str = request.form.get('relations')
        print(relations_str)
        local_time_str = request.form.get('local_time')

        send_message_to_user(socketio, user_id, "Upload completed and video generation started.")

        user_upload_folder = os.path.join(upload_folder, f"user_{user_id}")
        if os.path.exists(user_upload_folder):
            shutil.rmtree(user_upload_folder)
        os.makedirs(user_upload_folder, exist_ok=True)

        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join(user_upload_folder, filename))

        relations = json.loads(relations_str)
        moves_dict = get_movements_for_images_numbered(user_upload_folder, relations)
        print(moves_dict)
        split_moves = split_and_reverse_moves(moves_dict, user_upload_folder)
        print(split_moves)

        user_video_folder = os.path.join(generated_videos_folder, f'user_{user_id}')
        if os.path.exists(user_video_folder):
            shutil.rmtree(user_video_folder)
        os.makedirs(user_video_folder)

        for img_name, moves_list in sorted(split_moves.items(), key=lambda x: extract_number(x[0])):
            img_path = os.path.join(user_upload_folder, img_name)

            stop_event = threading.Event()
            progress_thread = threading.Thread(
                target=send_image_progress,
                args=(socketio, user_id, img_name, len(moves_list), stop_event),
                name=f"UPLOAD_THREAD_{user_id}"
            )
            progress_thread.start()

            user_progress_threads[user_id] = {
                'thread': progress_thread,
                'stop_event': stop_event
            }

            for move in moves_list:
                base_move = move.replace("-REVERSED", "")
                print(f"  Generating video with preset trajectory: {base_move} (original move: {move})")
                generate_video_from_image(img_path, user_id, base_move)
                print("Generated video: " + img_path + " " + user_id + " " + base_move)
                # time.sleep(5)

            stop_event.set()
            progress_thread.join()

        n = sum(len(moves) for moves in split_moves.values())
        latest_folders = get_latest_folders_with_file(user_video_folder, n=n)

        fuse_and_merge_video_folders(latest_folders, user_id)

        video_name_prefix = request.form.get('video_name_prefix', 'final_output_')
        upload_final_output_to_s3(user_id, socketio, local_time_str=local_time_str, video_name_prefix=video_name_prefix)

        clear_user_workspace(user_id)
        send_info_to_user(socketio, user_id, "Video generation process completed.")

        return {'status': 'success'}, 200

    finally:
        on_upload_complete(None, user_id)
