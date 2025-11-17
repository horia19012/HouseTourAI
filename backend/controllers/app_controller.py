import threading

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from services.auth_service import (
    authenticate_user,
    register_user
)
from services.upload_service import (
    handle_upload
)
from services.video_service import download_video_file, get_latest_video_for_download, get_latest_video_urls, \
    delete_video_file

app_controller = Blueprint('app_controller', __name__)


@app_controller.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    result, status = register_user(data)
    return jsonify(result), status


@app_controller.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    result, status = authenticate_user(data)
    return jsonify(result), status


@app_controller.route('/api/auth/validate-token', methods=['GET'])
@jwt_required()
def validate_token():
    current_user = get_jwt_identity()
    return jsonify({'valid': True, 'user': current_user}), 200


@app_controller.route('/api/upload', methods=['POST'])
@jwt_required()
def upload():
    current_user = get_jwt_identity()
    result, status = handle_upload(request, current_user)
    return jsonify(result), status


@app_controller.route('/api/download/<user_id>', methods=['GET'])
@jwt_required()
def download_video(user_id):
    current_user = get_jwt_identity()
    return download_video_file(current_user, user_id)


@app_controller.route('/api/latest-video/<user_id>', methods=['GET'])
@jwt_required()
def latest_video(user_id):
    current_user = get_jwt_identity()
    return get_latest_video_for_download(current_user, user_id)


@app_controller.route('/api/latest-videos-urls/<user_id>', methods=['GET'])
@jwt_required()
def latest_videos(user_id):
    current_user = get_jwt_identity()
    return get_latest_video_urls(current_user, user_id)


@app_controller.route('/api/delete-video', methods=['POST'])
@jwt_required()
def delete_video():
    current_user = get_jwt_identity()
    data = request.get_json()
    user_id = current_user
    s3_key = data.get('videoKey')
    result, status = delete_video_file(current_user, user_id, s3_key)
    return jsonify(result), status


@app_controller.route('/debug/threads', methods=['GET'])
def debug_threads():
    threads = threading.enumerate()
    thread_list = [{
        "name": t.name,
        "alive": t.is_alive(),
        "ident": t.ident
    } for t in threads]
    return jsonify({
        "thread_count": len(threads),
        "threads": thread_list
    })
