import os

from flask import send_file, jsonify

from extensions import socketio
from utils.s3 import (
    list_user_videos_sorted_by_date, s3_client, S3_BUCKET, process_video_on_s3, delete_video_from_s3
)
from utils.sockets import send_message_to_user


def download_video_file(current_user, user_id):
    if str(user_id) != str(current_user):
        return jsonify({"error": "Unauthorized access"}), 403

    send_message_to_user(socketio, user_id, "Your video download was initiated.")

    file_path = f'static/final_output/user_{user_id}/final_output.mp4'
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    try:
        return send_file(file_path, as_attachment=True, mimetype='video/mp4')
    except Exception as e:
        print(f"Download error: {e}")
        return jsonify({"error": "Unexpected error"}), 500


def get_latest_video_for_download(current_user, user_id):
    if str(user_id) != str(current_user):
        return jsonify({"error": "Unauthorized access"}), 403

    videos = list_user_videos_sorted_by_date(user_id)
    if not videos:
        return jsonify({"error": "No video found or failed to generate link"}), 404

    latest = videos[0]
    orig_url = latest['url']
    orig_key = orig_url.split(f".com/")[1]

    try:
        head_obj = s3_client.head_object(Bucket=S3_BUCKET, Key=orig_key)
        if head_obj.get('Metadata', {}).get('processed', '') != 'true':
            process_video_on_s3(orig_key)
    except Exception as ex:
        print(f"Could not check head_object or process: {ex}")
        process_video_on_s3(orig_key)

    return jsonify({
        'videoUrl': orig_url,
        'lastModified': latest['last_modified']
    })


def get_latest_video_urls(current_user, user_id):
    if str(user_id) != str(current_user):
        return jsonify({"error": "Unauthorized access"}), 403

    urls = list_user_videos_sorted_by_date(user_id)
    if urls:
        return jsonify({'latest_urls': urls})
    return jsonify({'error': 'No videos found'}), 404


def delete_video_file(current_user, user_id, s3_key):
    if str(user_id) != str(current_user):
        return {"error": "Unauthorized access"}, 403

    if not s3_key:
        return {"error": "No S3 key provided."}, 400

    success = delete_video_from_s3(s3_key)
    if success:
        return {"success": True}, 200
    else:
        return {"error": "Failed to delete file from S3."}, 500
