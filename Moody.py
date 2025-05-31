import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
import random

# Setup MIDI file and tracks
mid = MidiFile(ticks_per_beat=480)
main_track = MidiTrack()
background_track = MidiTrack()
percussion_track = MidiTrack()
mid.tracks.append(main_track)
mid.tracks.append(background_track)
mid.tracks.append(percussion_track)

# Tempo settings (slow jazz style)
bpm = 60
tempo = mido.bpm2tempo(bpm)
for track in [main_track, background_track, percussion_track]:
    track.append(MetaMessage('set_tempo', tempo=tempo))

# Instruments (MIDI program numbers)
main_instruments = {'piano': 0, 'harpsichord': 6, 'celesta': 8}
background_instruments = {'violin': 40, 'cello': 42, 'viola': 41}
percussion_instruments = {'kick': 36, 'snare': 38, 'closed_hh': 42}

main_instr_name, main_instr_prog = random.choice(list(main_instruments.items()))
background_instr_name, background_instr_prog = random.choice(list(background_instruments.items()))
percussion_channel = 9
print(f"Main instrument: {main_instr_name}")
print(f"Background instrument: {background_instr_name}")

channels = {'main': 0, 'background': 1, 'percussion': percussion_channel}

main_track.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main']))
background_track.append(Message('program_change', program=background_instr_prog, time=0, channel=channels['background']))

# Scales in three registers
scale = [60, 63, 65, 67, 70, 72]  # Cm pentatonic
high = [note + 12 for note in scale]
middle = scale
low = [note - 12 for note in scale]

# Helper: swing durations
def swing_durations(num_notes):
    return [300 if i % 2 == 0 else 180 for i in range(num_notes)]

# Generate dynamic pattern with transitions
def generate_dynamic_melody(length):
    melody = []
    registers = [low, middle, high]
    prev_register = random.choice(registers)
    consecutive_registers = 0
    prev_note = None
    pitch_history = []

    for i in range(length):
        if consecutive_registers >= 2:
            available = [r for r in registers if r != prev_register]
            if prev_register == high:
                available = [middle, low]
            elif prev_register == low:
                available = [middle, high]
            elif prev_register == middle:
                available = [low, high]
            new_register = random.choice(available)
            consecutive_registers = 0
        else:
            new_register = prev_register if random.random() < 0.5 else random.choice(registers)

        # Ensure register pattern transition does not repeat > 2x
        if len(pitch_history) >= 2 and pitch_history[-1] == pitch_history[-2] == new_register:
            options = [r for r in registers if r != new_register]
            new_register = random.choice(options)

        note = random.choice(new_register)

        # Avoid repeating the same note more than twice
        if len(melody) >= 2 and melody[-1] == melody[-2] == note:
            options = [n for n in new_register if n != note]
            if options:
                note = random.choice(options)

        # If current note is high, ensure a low note comes next or after next
        if prev_note in high:
            if i + 1 < length:
                melody.append(note)
                next_note = random.choice(low)
                melody.append(next_note)
                pitch_history.append(new_register)
                pitch_history.append(low)
                prev_note = next_note
                continue

        melody.append(note)
        pitch_history.append(new_register)
        prev_note = note

        if new_register == prev_register:
            consecutive_registers += 1
        else:
            consecutive_registers = 1
            prev_register = new_register

    return melody[:length]

# Generate background melody with register shift alignment
def generate_background_melody(main_melody):
    harmony = []
    for note in main_melody:
        harmony_note = note - 4 if note - 4 in low + middle + high else note
        harmony.append(harmony_note)
    return harmony

# Add percussion (simple repeated pattern)
def add_percussion(track, bars=16):
    kick, snare, hh = percussion_instruments['kick'], percussion_instruments['snare'], percussion_instruments['closed_hh']
    ticks = 480
    for bar in range(bars):
        for beat in range(4):
            time = 0 if bar == beat == 0 else ticks
            note = kick if beat % 2 == 0 else snare
            track.append(Message('note_on', note=note, velocity=50, time=time, channel=channels['percussion']))
            track.append(Message('note_off', note=note, velocity=0, time=120, channel=channels['percussion']))
            track.append(Message('note_on', note=hh, velocity=30, time=60, channel=channels['percussion']))
            track.append(Message('note_off', note=hh, velocity=0, time=60, channel=channels['percussion']))

# Total structure
total_bars = 16
notes_per_bar = 8
total_notes = total_bars * notes_per_bar
main_melody = generate_dynamic_melody(total_notes)
background_melody = generate_background_melody(main_melody)

# Add notes to tracks
def add_notes(track, channel, melody, is_main=False):
    durations = swing_durations(len(melody))
    for i, note in enumerate(melody):
        velocity = random.randint(80, 110) if is_main else random.randint(40, 60)
        delay = random.randint(-10, 10)
        track.append(Message('note_on', note=note, velocity=velocity, time=delay if i == 0 else 0, channel=channel))
        track.append(Message('note_off', note=note, velocity=0, time=durations[i]-delay, channel=channel))

add_notes(main_track, channels['main'], main_melody, is_main=True)
add_notes(background_track, channels['background'], background_melody)
add_percussion(percussion_track, total_bars)

filename = f"{random.randint(100000,999999)}.mid"
mid.save(filename)
print(f"Saved {filename}")
