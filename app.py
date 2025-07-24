from flask import Flask, render_template, request, jsonify
import cv2
import numpy as np
import os
from fer import FER
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import urllib.request
import bz2
import base64

app = Flask(__name__)

# Setup
UPLOAD_FOLDER = 'static'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Dlib model download
def download_dlib_model():
    if not os.path.exists("shape_predictor_68_face_landmarks.dat"):
        print("⬇ Downloading dlib face landmark model...")
        url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
        urllib.request.urlretrieve(url, "model.bz2")
        with bz2.BZ2File("model.bz2") as fr, open("shape_predictor_68_face_landmarks.dat", "wb") as fw:
            fw.write(fr.read())
        print("✅ Model downloaded.")

download_dlib_model()

# Spotify Auth
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id='9d593bb822b240168aee4fc1c79b2079',
    client_secret='770100d4ab5a49d498c8303067b48d32'
))

# Mappings
emotion_to_genre = {
    'angry': 'metal', 'disgust': 'punk', 'fear': 'ambient', 'happy': 'pop',
    'sad': 'blues', 'surprise': 'electronic', 'neutral': 'classical',
    'excited': 'edm', 'calm': 'lofi'
}

language_to_market = {
    'en': 'US', 'hi': 'IN', 'te': 'IN', 'ta': 'IN',
    'kn': 'IN', 'ml': 'IN', 'bn': 'IN', 'mr': 'IN', 'gu': 'IN'
}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    image_data = data['image'].split(',')[1]
    language = data['language']
    artist = data['artist']
    market = language_to_market.get(language, 'IN')

    # Decode base64 image
    img_bytes = base64.b64decode(image_data)
    img_np = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Emotion detection
    emotion_detector = FER(mtcnn=False)
    emotion, score = emotion_detector.top_emotion(img_rgb)

    if not emotion:
        return jsonify({
            'error': 'No emotion detected. Please try again with a clear face image.'
        })

    print(f"🧠 Detected Emotion: {emotion}, Confidence: {score}")
    genre = emotion_to_genre.get(emotion, 'pop')
    results = []

    # Try artist search
    print(f"🎤 Searching for artist: {artist}")
    query = sp.search(q=artist, type='track', market=market, limit=5)
    tracks = query['tracks']['items']

    if not tracks:
        print("⚠️ No results for artist. Trying genre fallback.")
        recs = sp.recommendations(seed_genres=[genre], limit=5, market=market)
        tracks = recs['tracks']

    for track in tracks:
        title = f"{track['name']} {', '.join([a['name'] for a in track['artists']])}"
        yt = VideosSearch(title, limit=1).result()
        yt_link = yt['result'][0]['link'] if yt['result'] else ''

        results.append({
            'name': track['name'],
            'artists': ', '.join([a['name'] for a in track['artists']]),
            'album': track['album']['name'],
            'url': track['external_urls']['spotify'],
            'preview': track['preview_url'],
            'youtube': yt_link
        })

    return jsonify({
        'emotion': emotion,
        'confidence': score,
        'tracks': results
    })

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

