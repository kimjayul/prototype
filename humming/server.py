# server.py
# -*- coding: utf-8 -*-

"""
==============================================================================
 AI 허밍 기반 자동 반주 생성 API 서버 (v1.0 - 최종 완성본)
==============================================================================
이 서버는 Flask를 기반으로 하며, React 프론트엔드로부터 요청을 받아
오디오 분석, 프롬프트 생성, AI 모델 호출의 전체 파이프라인을 실행하고
결과물인 음악 파일을 반환합니다.

[실행 방법]
1. Anaconda Prompt에서 가상환경 활성화: conda activate music_api_project
2. 서버 실행: python server.py
"""

# --- 1. 라이브러리 임포트 ---
import os
import random
import base64
import werkzeug.utils

# Flask 및 웹 관련
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# 오디오 및 음악 분석
import librosa
import numpy as np
import mido
from music21 import converter, analysis, tempo

# Google Cloud AI
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


# --- 2. Flask 애플리케이션 설정 ---
app = Flask(__name__)
# CORS(Cross-Origin Resource Sharing) 설정:
# 다른 주소(localhost:5173)에서 실행되는 React 앱의 요청을 허용합니다.
CORS(app)

# 파일 업로드 및 결과물 저장을 위한 폴더 설정
UPLOAD_FOLDER = 'uploads'
GENERATED_FOLDER = 'generated'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_FOLDER, exist_ok=True)


# --- 3. Helper 함수 ---
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
def midi_to_note_name(midi_note):
    """MIDI 노트 번호를 음이름으로 변환합니다."""
    octave = (midi_note // 12) - 1
    note_index = midi_note % 12
    return f"{NOTE_NAMES[note_index]}{octave}"


# --- 4. 백엔드 핵심 기능 함수들 ---

def audio_to_midi(input_audio_path, output_midi_path):
    """[파이프라인 1단계: 오디오 -> MIDI]"""
    print(f"[1단계 시작] 오디오 분석 및 멜로디 추출...")
    # (세부 로직은 이전과 동일하며, streamlit 관련 코드(st.info)만 print로 변경)
    y, sr = librosa.load(input_audio_path, sr=22050)
    f0, _, _ = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))
    times = librosa.times_like(f0, sr=sr)
    notes = []
    min_note_duration = 0.1
    current_note_start_time = None
    current_note_pitches = []
    for i, time in enumerate(times):
        is_voiced = not np.isnan(f0[i])
        if is_voiced:
            if current_note_start_time is None: current_note_start_time = time
            current_note_pitches.append(f0[i])
        else:
            if current_note_start_time is not None:
                duration = time - current_note_start_time
                if duration >= min_note_duration:
                    median_pitch_hz = np.median(current_note_pitches)
                    midi_note = int(round(librosa.hz_to_midi(median_pitch_hz)))
                    notes.append((current_note_start_time, duration, midi_note, 100))
                current_note_start_time = None
                current_note_pitches = []
    if not notes: raise Exception("오디오 파일에서 노트를 감지할 수 없습니다.")
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    ticks_per_beat = mid.ticks_per_beat
    tempo_val = mido.bpm2tempo(120)
    last_event_time_sec = 0
    for start_sec, duration_sec, pitch, velocity in notes:
        delta_ticks = mido.second2tick(start_sec - last_event_time_sec, ticks_per_beat, tempo_val)
        track.append(mido.Message('note_on', note=pitch, velocity=velocity, time=int(delta_ticks)))
        duration_ticks = mido.second2tick(duration_sec, ticks_per_beat, tempo_val)
        track.append(mido.Message('note_off', note=pitch, velocity=velocity, time=int(duration_ticks)))
        last_event_time_sec = start_sec + duration_sec
    mid.save(output_midi_path)
    print(f"[1단계 완료] 멜로디 MIDI 파일 저장 성공: {output_midi_path}")
    return True

def midi_to_text_prompt_advanced(midi_path, genre, mood, instruments, custom_prompt):
    """[파이프라인 2단계: MIDI -> Text]"""
    print(f"[2단계 시작] MIDI 파일과 사용자 선택을 조합하여 프롬프트 생성...")
    score = converter.parse(midi_path)
    melody_part = score.parts[0]
    key = melody_part.analyze('key')
    key_name = f"{key.tonic.name} {key.mode}"
    tempo_bpm = 120
    if melody_part.getElementsByClass(tempo.MetronomeMark):
        tempo_bpm = melody_part.getElementsByClass(tempo.MetronomeMark)[0].getQuarterBPM()
    note_durations = [n.duration.quarterLength for n in melody_part.flatten().notesAndRests if n.isNote]
    avg_duration = sum(note_durations) / len(note_durations) if note_durations else 1.0
    rhythm_desc = "a slow and lyrical rhythm"
    if avg_duration < 0.5: rhythm_desc = "a fast and lively rhythm"
    elif avg_duration < 1.0: rhythm_desc = "a moderately paced rhythm"
    pitches = [p.pitch.midi for p in melody_part.flatten().notes]
    intervals = [pitches[i] - pitches[i-1] for i in range(1, len(pitches))]
    upward_movement, downward_movement = sum(i > 0 for i in intervals), sum(i < 0 for i in intervals)
    contour_desc = "a relatively static contour"
    if upward_movement > downward_movement * 1.5: contour_desc = "a predominantly ascending contour"
    elif downward_movement > upward_movement * 1.5: contour_desc = "a predominantly descending contour"
    elif upward_movement + downward_movement > len(pitches) / 2: contour_desc = "a dynamic and varied contour"
    
    instrument_text = ", ".join(instruments)
    base_prompt = ""
    if len(instruments) == 1:
        base_prompt = f"Generate a high-quality music piece for a SOLO {instrument_text}. The style should be a {genre} with a {mood} mood. CRITICAL INSTRUCTION: Use ONLY the {instrument_text} and no other instruments."
    else:
        base_prompt = f"Generate a professional, high-quality instrumental piece in a {genre} style with a {mood} mood. CRITICAL INSTRUCTION: Use ONLY the following instruments: {instrument_text}."
    
    analysis_prompt = f" The music should be based on a user's humming, with these core characteristics: Key: approximately {key_name}. Tempo: around {round(tempo_bpm)} BPM. Rhythm: {rhythm_desc}. Melody Contour: {contour_desc}."
    final_prompt = base_prompt + analysis_prompt
    if custom_prompt: final_prompt += f" Additionally, please follow this special user request: '{custom_prompt}'"
    creative_spices = ["with a slightly unexpected chord progression.", "in a lo-fi style.", "featuring a surprising key change.", "with a minimalist approach."]
    final_prompt += f" For a creative touch, please interpret this {random.choice(creative_spices)}"
    print("[2단계 완료] 프롬프트 생성 성공.")
    return final_prompt

def generate_music_with_api(text_prompt, output_audio_path, project_id, location="us-central1"):
    """[파이프라인 3단계: Text -> Music]"""
    print(f"[3단계 시작] Google Cloud Lyria API 호출...")
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    instance_dict = {"prompt": text_prompt}
    instance = json_format.ParseDict(instance_dict, Value())
    instances = [instance]
    parameters_dict = {"temperature": 0.95, "seed": random.randint(0, 2**32 - 1)}
    parameters = json_format.ParseDict(parameters_dict, Value())
    publisher_endpoint = "publishers/google/models/lyria-002"
    endpoint_path = f"projects/{project_id}/locations/{location}/{publisher_endpoint}"
    print(f"Lyria 모델에 요청 (Seed: {parameters_dict['seed']})")
    response = client.predict(endpoint=endpoint_path, instances=instances, parameters=parameters)
    predictions = response.predictions
    if not predictions: raise Exception("API가 아무런 결과물을 반환하지 않았습니다.")
    prediction_result = dict(predictions[0])
    encoded_audio = prediction_result['bytesBase64Encoded']
    audio_data = base64.b64decode(encoded_audio)
    with open(output_audio_path, 'wb') as f:
        f.write(audio_data)
    print(f"[3단계 완료] API로부터 생성된 오디오 파일 저장 성공: {output_audio_path}")
    return True


# --- 5. API 엔드포인트(주소) 정의 ---

@app.route('/generate-music', methods=['POST'])
def generate_music_endpoint():
    """React 프론트엔드로부터 요청을 받아 전체 음악 생성 파이프라인을 실행합니다."""
    print("\n--- 프론트엔드로부터 새로운 음악 생성 요청 수신 ---")
    try:
        # 1. 프론트엔드에서 보낸 데이터(파일, 옵션)를 받습니다.
        if 'audio' not in request.files: return jsonify({"error": "오디오 파일이 없습니다."}), 400
        audio_file = request.files['audio']
        genre = request.form.get('genre')
        mood = request.form.get('mood')
        instruments = request.form.getlist('instruments[]')
        custom_prompt = request.form.get('custom_prompt')

        # 2. 업로드된 오디오 파일을 서버에 저장합니다.
        filename = werkzeug.utils.secure_filename(audio_file.filename)
        audio_path = os.path.join(UPLOAD_FOLDER, filename)
        audio_file.save(audio_path)

        # 3. 정의된 파이프라인 함수들을 순차적으로 호출합니다.
        temp_midi_path = os.path.join(GENERATED_FOLDER, "temp.mid")
        audio_to_midi(audio_path, temp_midi_path)

        text_prompt = midi_to_text_prompt_advanced(temp_midi_path, genre, mood, instruments, custom_prompt)
        
        gcp_project_id = os.environ.get('GCP_PROJECT_ID') # 환경 변수에서 프로젝트 ID 읽기
        if not gcp_project_id: raise Exception("GCP_PROJECT_ID 환경 변수가 설정되지 않았습니다.")
        
        final_audio_filename = f"generated_{werkzeug.utils.secure_filename(os.path.splitext(filename)[0])}_{random.randint(1000,9999)}.wav"
        final_audio_path = os.path.join(GENERATED_FOLDER, final_audio_filename)

        generate_music_with_api(text_prompt, final_audio_path, gcp_project_id)
        
        # 4. 성공 시, 프론트엔드에 생성된 파일의 URL을 포함한 JSON 응답을 보냅니다.
        print("--- 음악 생성 성공! 프론트엔드에 결과 반환 ---")
        return jsonify({
            "status": "success",
            "message": "음악이 성공적으로 생성되었습니다.",
            "audio_url": f"/music/{final_audio_filename}"
        })
    except Exception as e:
        # 5. 실패 시, 구체적인 오류 메시지를 포함한 JSON 응답을 보냅니다.
        print(f"!!! 파이프라인 실행 중 오류 발생: {e} !!!")
        return jsonify({"error": str(e)}), 500

@app.route('/music/<path:filename>')
def serve_music(filename):
    """'generated' 폴더에 저장된 음악 파일을 프론트엔드에서 접근할 수 있게 해줍니다."""
    return send_from_directory(GENERATED_FOLDER, filename)


# --- 6. 서버 실행 ---
if __name__ == '__main__':
    # !!! 중요 !!!
    # GCP 인증을 위한 환경 변수를 설정합니다. 
    # 아래 경로를 자신의 JSON 키 파일 경로로 반드시 수정하세요.
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "my-music-project-471519-4f8b52e299a4.json"
    
    # GCP 프로젝트 ID도 환경 변수로 설정합니다.
    # 아래 ID를 자신의 GCP 프로젝트 ID로 반드시 수정하세요.
    os.environ['GCP_PROJECT_ID'] = "my-music-project-471519"
    
    # 서버를 실행합니다. debug=True는 개발 중에 코드가 바뀌면 서버가 자동 재시작되게 합니다.
    # host='0.0.0.0'은 컴퓨터의 모든 IP 주소에서 접속을 허용합니다.
    app.run(host='0.0.0.0', port=5000, debug=True)