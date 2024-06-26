import numpy as np
import os
import librosa
import torchaudio

# Function to check if an audio file is readable and its duration is greater than 500ms
def is_audio_valid(audio_path, threshold_ms=500, n_fft=160):
    try:
        # n_fft=160 is too large for uncentered analysis of input signal of length=156

        waveform, sample_rate = torchaudio.load(audio_path)
        duration_ms = waveform.size(1) / sample_rate * 1000  # Duration in milliseconds
        signal_length = waveform.size(1)

        return duration_ms >= threshold_ms and signal_length >= n_fft
    except:
        return False


# # Function to clip SFCCs into 50-framed tensors and save them as files
# def clip_and_save_if(sfcc_path, label, save_dir, frame_length=50, overlap_ratio=0.5):
#     sfcc = np.loadtxt(sfcc_path)
#     _, total_frames = sfcc.shape
#     overlap = int(overlap_ratio * frame_length)
    
#     paths = []
#     for frame_idx in range(0, total_frames, overlap):
#         if frame_idx + frame_length > total_frames:
#             break
#         segment = sfcc[:, frame_idx:frame_idx + frame_length]
#         # Generate a unique filename based on the sfcc_path
#         filename = os.path.basename(sfcc_path).replace('.sfcc', f'_{frame_idx}_sfcc.npy')
#         save_path = os.path.join(save_dir, filename)
#         # Save the SFCC segment data
#         np.save(save_path, segment)
#         paths.append({'sfcc_path': save_path, 'label': label})
#     return paths

# Function to calculate instantaneous frequency
def calculate_instantaneous_frequency(signal, n_fft, hop_length):
    stft = librosa.stft(signal.cpu().reshape(-1).numpy(), n_fft=n_fft, hop_length=hop_length, win_length=n_fft, center=False)
    num_bins, num_frames = stft.shape
    #print(stft.shape)
    instantaneous_frequency = np.zeros_like(stft, dtype=np.float32)

    for l in range(num_frames - 1):
        for k in range(num_bins):
            next_stft = stft[k, l+1]
            phase_diff = np.angle(np.conj(stft[k, l]) * next_stft)
            instantaneous_frequency[k, l] = phase_diff / (2 * np.pi)

    return instantaneous_frequency

# Function to calculate and save instantaneous frequency
def calculate_and_save_instantaneous_frequency(audio_path, n_fft, hop_length, overlap_ratio, frame_length, save_dir):
    waveform, _ = torchaudio.load(audio_path)
    instantaneous_frequency = calculate_instantaneous_frequency(waveform, n_fft, hop_length)
    #print(instantaneous_frequency.shape)
    _, total_frames = instantaneous_frequency.shape
    overlap = int(overlap_ratio*frame_length)
    # print((total_frames - frame_length) // overlap)
    
    filenames = []
    for frame_idx in range(0, total_frames, overlap):
        
        if frame_idx+frame_length > total_frames:
            break
        
        segment = instantaneous_frequency[:, frame_idx:frame_idx+frame_length]
        # Generate a unique filename based on the audio_path
        filename = os.path.basename(audio_path) + f'{frame_idx}' + "_instant_frequency.npy"
        save_path = os.path.join(save_dir, filename)
        # Save the instantaneous frequency data
        np.save(save_path, segment)
        filenames.append(filename)
    # print(f"Saved {len(paths)} instantaneous frequency segments")
    return filenames