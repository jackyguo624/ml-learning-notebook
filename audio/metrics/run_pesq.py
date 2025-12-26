import numpy as np
import librosa
import soundfile as sf
from pesq import pesq

def generate_audio():

    # Generate synthetic "speech" (just for mechanical test, PESQ won't be valid perceptually but will run)
    filename = "speech_sample_v0.wav"
    sr = 16000
    t = np.linspace(0, 3, 3*sr)
    audio = 0.5 * np.sin(2*np.pi*440*t) * np.exp(-t) + 0.3 * np.sin(2*np.pi*880*t)
    sf.write(filename, audio, sr)
    print("Generated synthetic audio.")

    # Load audio at 16k for wb-PESQ or 8k for nb-PESQ
    target_sr = 16000 
    y, sr = librosa.load(filename, sr=target_sr, mono=True)
    return y, sr

def add_noise(audio, snr_db=10):
    # Calculate signal power
    sig_power = np.mean(audio ** 2)
    # Calculate noise power
    noise_power = sig_power / (10 ** (snr_db / 10))
    # Generate noise
    noise = np.random.normal(0, np.sqrt(noise_power), audio.shape)
    return audio + noise

def time_shift(audio, shift_ms, sr):
    shift_samples = int(shift_ms * sr / 1000)
    shifted = np.roll(audio, shift_samples)
    # If we want a "real" shift (zeros introduced), we should use padding/slicing
    # But np.roll is a cyclic shift. For checking alignment issues, cyclic might mask it if checked against itself,
    # but PESQ handles delays. However, let's do a linear shift with zero padding.
    output = np.zeros_like(audio)
    if shift_samples > 0:
        output[shift_samples:] = audio[:-shift_samples]
    elif shift_samples < 0:
        output[:shift_samples] = audio[-shift_samples:]
    else:
        output = audio
    return output

def main():
    print("Loading audio...")
    ref, sr = generate_audio()
    print(f"Loaded audio: {len(ref)/sr:.2f}s at {sr}Hz")

    # PESQ requires 16k or 8k. We loaded at 16k.
    
    # 1. Generate v1: Noisy
    print("Generating v1 (Noisy)...")
    v1 = add_noise(ref, snr_db=10)
    # dump to file v1.wav
    sf.write("speech_sample_v1.wav", v1, sr)
    
    # 2. Generate v2: Time Shifted
    print("Generating v2 (Shifted 200ms)...")
    v2 = time_shift(ref, shift_ms=200, sr=sr)
    # dump to file v2.wav
    sf.write("speech_sample_v2.wav", v2, sr)
    
    # Calculate PESQ
    # pesq(fs, ref, deg, 'wb' or 'nb')
    # fs must be 16000 or 8000
    
    print("\nCalculating PESQ scores...")
    
    score_v0 = pesq(sr, ref, ref, 'wb')
    print(f"PESQ (Reference vs Reference v0): {score_v0:.4f}")
    
    score_v1 = pesq(sr, ref, v1, 'wb')
    print(f"PESQ (Reference vs Noisy v1): {score_v1:.4f}")
    
    score_v2 = pesq(sr, ref, v2, 'wb')
    print(f"PESQ (Reference vs Shifted v2): {score_v2:.4f}")

if __name__ == "__main__":
    main()
