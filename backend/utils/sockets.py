import os
import time

import requests
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL")

current_uploader = None
waiting_users = set()


def send_message_to_user(socketio, user_id, message):
    user_id_str = str(user_id)
    print(f"[SEND MESSAGE] To {user_id_str}: {message}")

    socketio.emit('message', {'msg': message}, room=user_id_str)


def send_warning_to_user(socketio, user_id, message):
    user_id_str = str(user_id)
    print(f"[SEND WARNING] To {user_id_str}: {message}")

    socketio.emit('warning', {'msg': message}, room=user_id_str)


def send_info_to_user(socketio, user_id, message):
    socketio.emit('info', {'msg': message}, room=user_id)


def send_image_progress(socketio, user_id, img_name, total_moves, stop_event):
    """
    Sends periodic progress updates while all moves for a single image are processed.
    Progress increases up to 95% over total estimated time.

    """

    load_dotenv()

    video_gen_time = int(os.getenv("VIDEO_GENERATION_TIME"))

    total_time = total_moves * video_gen_time
    update_interval = 10
    max_progress = 95
    progress = 10

    updates_count = max_progress // 10
    seconds_per_update = total_time / updates_count

    while progress < max_progress and not stop_event.is_set():
        send_message_to_user(socketio, user_id, f"Processing {img_name}: {progress}% completed")
        progress += 10
        time.sleep(seconds_per_update)

    while not stop_event.is_set():
        send_message_to_user(socketio, user_id, f"Processing {img_name}: 95% completed (finalizing)")
        time.sleep(seconds_per_update)

    send_message_to_user(socketio, user_id, f"Processing {img_name}: 100% completed")
    print(f"Progress {img_name}: 100%")


def check_and_handle_running_uploads(socketio, user_id):
    global current_uploader, waiting_users

    try:
        response = requests.get(f"{API_URL}/debug/threads")
        response.raise_for_status()
        running_threads = response.json().get("threads", [])
        alive_thread_names = [t["name"] for t in running_threads if t.get("alive")]
        print(f"Running thread names: {alive_thread_names}")
    except Exception as e:
        print(f"Error fetching thread info: {e}")
        return None

    user_id_str = str(user_id)
    user_upload_thread = f"UPLOAD_THREAD_{user_id_str}"

    upload_threads = [name for name in alive_thread_names if name.startswith("UPLOAD_THREAD_")]

    # Case 1: This user's upload thread is running
    if user_upload_thread in upload_threads:
        current_uploader = user_id
        send_warning_to_user(socketio, user_id, "You already have an ongoing upload. Please wait for it to finish.")
        return {"status": "busy", "message": "You already have an ongoing upload."}, 429

    # Case 2: Someone else's upload thread is running
    for thread_name in upload_threads:
        if thread_name != user_upload_thread:
            current_uploader = thread_name.replace("UPLOAD_THREAD_", "")
            waiting_users.add(user_id)
            send_warning_to_user(socketio, user_id, "Another upload is in progress. Please wait for your turn.")
            return {"status": "queue", "message": "Another upload is in progress."}, 429

    # Case 3: No uploads running
    current_uploader = user_id
    return None


def on_upload_complete(socketio, user_id):
    global current_uploader, waiting_users

    if user_id == current_uploader:
        print(f"Upload complete for {user_id}")
        current_uploader = None

        for user in list(waiting_users):
            send_info_to_user(socketio, user, "Upload slot is now free. You can now upload.")
        waiting_users.clear()
