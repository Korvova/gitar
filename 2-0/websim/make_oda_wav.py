import numpy as np, wave
SR = 44100
F = {"C": 261.63, "D": 293.66, "E": 329.63, "F": 349.23, "G": 392.00}
bpm = 90.0
q = 60.0 / bpm
# Ода к радости: ми ми фа соль | соль фа ми ре | до до ре ми | ми. ре ре(половинная)
notes = [("E", 1), ("E", 1), ("F", 1), ("G", 1), ("G", 1), ("F", 1), ("E", 1), ("D", 1),
         ("C", 1), ("C", 1), ("D", 1), ("E", 1), ("E", 1.5), ("D", 0.5), ("D", 2)]

def pluck(freq, dur):
    """Карплус-Стронг: щипок струны."""
    n = int(SR * dur)
    period = int(SR / freq)
    buf = np.random.uniform(-1, 1, period)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = 0.996 * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return out

track = []
for name, beats in notes:
    track.append(pluck(F[name], beats * q))
track.append(np.zeros(int(SR * 0.8)))
x = np.concatenate(track)
x = x / np.max(np.abs(x)) * 0.8
path = r"C:\Users\AdminPC\AppData\Local\Temp\claude\C--App-gitar\126b7772-aef3-4dca-9ad4-7710c4149d82\scratchpad\oda_k_radosti.wav"
with wave.open(path, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes())
print("ok", len(x) / SR, "s")
