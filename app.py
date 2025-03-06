from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import datetime
import os
import logging
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend to call API

# Path to the Python script to run
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logs

# Path to the Python script to run
SCRIPT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'check-host.py'))


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "data": "GET DATA"
    }), 200

@app.route('/check', methods=['POST'])
def check_host():
    data = request.get_json()
    target = data.get('target')

    if not target:
        return jsonify({
            "timestamp": get_current_time(),
            "error": "Missing 'target' in request."
        }), 400
    # if not is_valid_target(target):
    #         logging.warning(f"Định dạng 'target' không hợp lệ: {target}")
    #         return jsonify({
    #             "timestamp": get_current_time(),
    #             "error": "Định dạng 'target' không hợp lệ. Vui lòng cung cấp URL hoặc địa chỉ IP hợp lệ."
    #         }), 400
    try:
        # Prepare the command to execute the script with the HTTP flag
        cmd = ['/usr/bin/python3', SCRIPT_PATH, '--http', '-t', target]

        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        script_dir = os.path.dirname(SCRIPT_PATH)
        parent_dir = os.path.abspath(os.path.join(script_dir, '..'))
        env['PYTHONPATH'] = parent_dir + os.pathsep + env.get('PYTHONPATH', '')

        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=script_dir,
            env=env  # Pass the modified environment
        )
        output = result.stdout.strip()
        try:
            parsed_output = json.loads(output)
            # Lúc này "parsed_output" là 1 list (mảng) hoặc dict tùy nội dung
        except json.JSONDecodeError:
            # Nếu parse thất bại => script trả về chuỗi không phải JSON
            return jsonify({"error": "Invalid JSON from script", "raw": output}), 500

        return jsonify({
            "status": 200,
            "message": "Get data success",
            "data": parsed_output
        }), 200
    except subprocess.CalledProcessError as e:
        error_output = e.stderr.strip() or e.stdout.strip()
        logging.error(f"Subprocess error: {error_output}")
        return jsonify({
            "timestamp": get_current_time(),
            "error": error_output,
        }), 500
    except Exception as e:
        return jsonify({
            "timestamp": get_current_time(),
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

def get_current_time():
    return datetime.datetime.now().strftime("%H:%M:%S")

if __name__ == '__main__':
    app.run(debug=True, port=5001)
