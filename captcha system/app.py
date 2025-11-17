from flask import Flask, request, send_from_directory, jsonify, url_for
import math, json, os, uuid
import numpy as np
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')

LOG_FILE = 'attempts_log.jsonl'
IMAGES_DIR = os.path.join(app.root_path, 'static', 'images')

def save_log(record):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def extract_features(events):
    if not events or len(events) < 2:
        return None
    ts = np.array([e['t'] for e in events], dtype=float)
    xs = np.array([e['x'] for e in events], dtype=float)
    ys = np.array([e['y'] for e in events], dtype=float)

    dt = np.diff(ts) / 1000.0
    dx = np.diff(xs)
    dy = np.diff(ys)
    dist = np.sqrt(dx*dx + dy*dy)
    speed = dist / (dt + 1e-6)
    accel = np.diff(speed) / (dt[1:] + 1e-6) if len(speed) > 1 else np.array([0.0])

    total_time_ms = float(ts[-1] - ts[0])
    path_length = float(np.sum(dist))
    euclidean = float(math.hypot(xs[-1]-xs[0], ys[-1]-ys[0]))
    straightness = euclidean / (path_length + 1e-6)

    pause_threshold = 8.0
    pause_mask = speed < pause_threshold
    pause_count = int(np.sum(pause_mask))
    jitter_std = float(np.std(dist - np.mean(dist))) if len(dist) > 0 else 0.0

    features = {
        'total_time_ms': total_time_ms,
        'n_points': int(len(ts)),
        'mean_speed': float(np.mean(speed)) if len(speed)>0 else 0.0,
        'std_speed': float(np.std(speed)) if len(speed)>0 else 0.0,
        'mean_accel': float(np.mean(accel)) if len(accel)>0 else 0.0,
        'std_accel': float(np.std(accel)) if len(accel)>0 else 0.0,
        'path_length': path_length,
        'euclidean': euclidean,
        'straightness': straightness,
        'pause_count': pause_count,
        'jitter_std': jitter_std
    }
    return features

def human_rule_check(features, pixel_distance):
    if pixel_distance > 14:
        return False, "position_mismatch"
    if features['total_time_ms'] < 200:
        return False, "too_fast"
    if features['straightness'] > 0.985 and features['std_speed'] < 1.2:
        return False, "too_straight_or_low_speed_variation"
    if features['jitter_std'] < 0.6 and features['std_speed'] < 0.8:
        return False, "low_jitter"
    if features['n_points'] < 6:
        return False, "too_few_points"
    return True, "passed"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json(force=True)
    session_id = data.get('session_id', str(uuid.uuid4()))
    events = data.get('events', [])
    pixel_distance = float(data.get('pixel_distance', 9999))

    features = extract_features(events)
    if features is None:
        return jsonify({'ok': False, 'reason': 'too_few_events'}), 400

    is_human, reason = human_rule_check(features, pixel_distance)
    record = {
        'ts': datetime.utcnow().isoformat(),
        'session_id': session_id,
        'payload': {k:v for k,v in data.items() if k!='events'},
        'features': features,
        'is_human': bool(is_human),
        'reason': reason
    }
    save_log(record)
    return jsonify({'ok': True, 'human': bool(is_human), 'features': features, 'reason': reason})

@app.route('/images', methods=['GET'])
def list_images():
    try:
        files = []
        for fname in os.listdir(IMAGES_DIR):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
                files.append(fname)
        files.sort()
        urls = [url_for('static', filename=f'images/{f}') for f in files]
        return jsonify({'ok': True, 'images': urls})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask app on http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)

