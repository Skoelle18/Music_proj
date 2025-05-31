import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
import random

# Setup MIDI file and tracks
mid = MidiFile(ticks_per_beat=480)
main_track = MidiTrack()
main_layer2 = MidiTrack()
main_layer3 = MidiTrack()
background_track = MidiTrack()
percussion_track = MidiTrack()
second_melody_track = MidiTrack()
mid.tracks.extend([main_track, main_layer2, main_layer3, background_track, percussion_track, second_melody_track])

# Tempo settings (slow jazz style)
bpm = 75
tempo = mido.bpm2tempo(bpm)
for track in mid.tracks:
    track.append(MetaMessage('set_tempo', tempo=tempo))

# Instruments (MIDI program numbers)
main_instruments = {
    'acoustic_guitar': 24,
    'bright_acoustic_piano': 1,
    'celesta': 8,
    'vibraphone': 11,
    'electric_piano': 5,
    'warm_pad': 89,
    'soft_strings': 50
}
background_instruments = {
    'string_ensemble': 48,
    'clarinet': 71,
    'flute': 73,
    'oboe': 68,
    'french_horn': 60
}
percussion_instruments = {
    'kick': 36,
    'snare': 38,
    'closed_hh': 42,
    'open_hh': 46
}

main_instr_name, main_instr_prog = random.choice(list(main_instruments.items()))
background_instr_name, background_instr_prog = random.choice(list(background_instruments.items()))
percussion_channel = 9

print(f"Main instrument: {main_instr_name}")
print(f"Background instrument: {background_instr_name}")

channels = {
    'main': 0,
    'main2': 1,
    'main3': 2,
    'background': 3,
    'percussion': percussion_channel,
    'second': 4
}

main_track.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main']))
main_layer2.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main2']))
main_layer3.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main3']))
background_track.append(Message('program_change', program=background_instr_prog, time=0, channel=channels['background']))
second_melody_track.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['second']))

# Sad/depressing jazz scales (root C minor and related)
scales = {
    'C_natural_minor': [60, 62, 63, 65, 67, 68, 70, 72],       # C D Eb F G Ab Bb C
    'C_harmonic_minor': [60, 62, 63, 65, 67, 68, 71, 72],      # C D Eb F G Ab B C
    'C_dorian': [60, 62, 63, 65, 67, 69, 70, 72],              # C D Eb F G A Bb C
    'C_phrygian': [60, 61, 63, 65, 67, 68, 70, 72]             # C Db Eb F G Ab Bb C
}
scale_name, scale = random.choice(list(scales.items()))
print(f"Using scale: {scale_name}")

high = [note + 12 for note in scale]
middle = scale
low = [note - 12 for note in scale]
registers = [low, middle, high]

# Swing durations helper - alternating longer and shorter notes (slow swing)
def swing_durations(num_notes):
    durations = []
    base_long = 640  # ~1.3 beats
    base_short = 320 # ~0.7 beats
    for i in range(num_notes):
        durations.append(base_long if i % 2 == 0 else base_short)
    return durations

# Generate melody with register changes every 6 notes
def generate_register_changing_melody(length, segment_size=6):
    melody = []
    prev_register = random.choice(registers)
    total_segments = length // segment_size + (1 if length % segment_size else 0)

    for seg in range(total_segments):
        available_registers = [r for r in registers if r != prev_register]
        current_register = random.choice(available_registers)
        prev_register = current_register

        for i in range(segment_size):
            if len(melody) >= length:
                break
            note = random.choice(current_register)
            if melody:
                prev_note = melody[-1]
                if abs(note - prev_note) > 7:
                    close_notes = [n for n in current_register if abs(n - prev_note) <= 7]
                    if close_notes:
                        note = random.choice(close_notes)
            melody.append(note)
    return melody[:length]

# Background harmony generation adjusted to fit sad scale and avoid dissonance
def generate_background_melody(main_melody):
    harmony = []
    all_notes = low + middle + high
    for i, note in enumerate(main_melody):
        if i % 4 == 0:
            chord_tone = note - 3 if (note - 3) in all_notes else note  # minor third down
        elif i % 4 == 2:
            chord_tone = note + 7 if (note + 7) in all_notes else note  # perfect fifth up
        else:
            chord_tone = note + 4 if (note + 4) in all_notes else note  # major third up
        harmony.append(chord_tone)
    return harmony

def add_percussion(track, bars=16):
    kick, snare, hh_closed, hh_open = (
        percussion_instruments['kick'],
        percussion_instruments['snare'],
        percussion_instruments['closed_hh'],
        percussion_instruments['open_hh']
    )
    ticks = 480
    for bar in range(bars):
        for beat in range(4):
            note_time = ticks if not (bar == 0 and beat == 0) else 0
            if beat % 4 == 0:
                note = kick
                velocity = 60
            elif beat % 4 == 2:
                note = snare
                velocity = 50
            else:
                # Alternate closed and open hi-hats on off beats for swing
                note = hh_closed if beat % 2 == 1 else hh_open
                velocity = 35
            track.append(Message('note_on', note=note, velocity=velocity, time=note_time, channel=channels['percussion']))
            track.append(Message('note_off', note=note, velocity=0, time=120, channel=channels['percussion']))

def generate_complementary_melody(main_melody):
    complementary = []
    all_notes = low + middle + high
    for i, note in enumerate(main_melody):
        if i % 4 == 2:
            new_note = note + 3  # minor third up
        elif i % 4 == 0:
            new_note = note + 5  # perfect fourth up
        else:
            new_note = note
        complementary.append(new_note if new_note in all_notes else note)
    return complementary

def add_notes(track, channel, melody):
    durations = swing_durations(len(melody))
    for i, note in enumerate(melody):
        velocity = random.randint(30, 50)
        gap = 240 if i % 4 == 3 else 0  # breathe after each 4-note phrase
        track.append(Message('note_on', note=note, velocity=velocity, time=0 if i == 0 else gap, channel=channel))
        track.append(Message('note_off', note=note, velocity=0, time=durations[i], channel=channel))

# Structure
total_bars = 16
notes_per_bar = 8
total_notes = total_bars * notes_per_bar

# Generate melodies
main_melody = generate_register_changing_melody(total_notes, segment_size=6)
main_melody_low = [note - 12 if (note - 12) >= 40 else note for note in main_melody]
main_melody_high = [note + 12 if (note + 12) <= 84 else note for note in main_melody]
background_melody = generate_background_melody(main_melody)
second_melody = generate_complementary_melody(main_melody)

# Add notes to tracks
add_notes(main_track, channels['main'], main_melody)
add_notes(main_layer2, channels['main2'], main_melody_low)
add_notes(main_layer3, channels['main3'], main_melody_high)
add_notes(background_track, channels['background'], background_melody)
add_notes(second_melody_track, channels['second'], second_melody)

# Add percussion
add_percussion(percussion_track, total_bars)

# Save MIDI file
filename = f"{random.randint(100000,999999)}.mid"
mid.save(filename)
print(f"Saved {filename}")
