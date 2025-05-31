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

# Tempo settings (more upbeat jazz style)
bpm = 110  # increased tempo for upbeat feel
tempo = mido.bpm2tempo(bpm)
for track in mid.tracks:
    track.append(MetaMessage('set_tempo', tempo=tempo))

# Instruments (MIDI program numbers) - favor brighter instruments for upbeat sound
main_instruments = {'bright_acoustic_piano': 1, 'electric_piano': 5, 'vibraphone': 11, 'celesta': 8, 'acoustic_guitar': 24}
background_instruments = {'string_ensemble': 48, 'clarinet': 71, 'flute': 73}
percussion_instruments = {'kick': 36, 'snare': 38, 'closed_hh': 42, 'open_hh': 46}

main_instr_name, main_instr_prog = random.choice(list(main_instruments.items()))
background_instr_name, background_instr_prog = random.choice(list(background_instruments.items()))
percussion_channel = 9
print(f"Main instrument: {main_instr_name}")
print(f"Background instrument: {background_instr_name}")

channels = {'main': 0, 'main2': 1, 'main3': 2, 'background': 3, 'percussion': percussion_channel, 'second': 4}

main_track.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main']))
main_layer2.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main2']))
main_layer3.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main3']))
background_track.append(Message('program_change', program=background_instr_prog, time=0, channel=channels['background']))
second_melody_track.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['second']))

# Major scale (C major for bright happy sound)
major_scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C D E F G A B C

high = [note + 12 for note in major_scale]
middle = major_scale
low = [note - 12 for note in major_scale]
registers = [low, middle, high]

# Helper: swing durations with more pronounced swing (long-short)
def swing_durations(num_notes):
    # Longer first note, shorter second note, repeating
    return [320 if i % 2 == 0 else 160 for i in range(num_notes)]

# Generate melody with smoother register changes and focus on stepwise motion to sound joyful
def generate_register_changing_melody(length, segment_size=6):
    melody = []
    prev_register = random.choice(registers)
    total_segments = length // segment_size + (1 if length % segment_size else 0)

    for seg in range(total_segments):
        available_registers = [r for r in registers if r != prev_register]
        current_register = random.choice(available_registers)
        prev_register = current_register

        prev_note = None
        for i in range(segment_size):
            if len(melody) >= length:
                break
            if prev_note is None:
                note = random.choice(current_register)
            else:
                # Favor stepwise motion (±2 semitones) or small skips (±3 or ±4)
                possible_notes = [n for n in current_register if abs(n - prev_note) <= 4]
                note = random.choice(possible_notes) if possible_notes else random.choice(current_register)

            # Occasionally add a passing tone for excitement
            if random.random() < 0.15 and len(melody) > 0:
                passing_tone = note + (1 if random.random() < 0.5 else -1)
                if passing_tone in current_register:
                    melody.append(passing_tone)

            melody.append(note)
            prev_note = note
    return melody[:length]

def generate_background_melody(main_melody):
    harmony = []
    for i, note in enumerate(main_melody):
        if i % 4 == 0:
            chord_tone = note - 5 if (note - 5) in low + middle + high else note
        elif i % 4 == 2:
            chord_tone = note + 7 if (note + 7) in low + middle + high else note
        else:
            chord_tone = note + 4 if (note + 4) in low + middle + high else note
        harmony.append(chord_tone)
    return harmony

def add_percussion(track, bars=16):
    kick, snare, closed_hh, open_hh = percussion_instruments['kick'], percussion_instruments['snare'], percussion_instruments['closed_hh'], percussion_instruments['open_hh']
    ticks = 480
    for bar in range(bars):
        for beat in range(4):
            time = ticks if not (bar == 0 and beat == 0) else 0

            # Kick on beats 1 and 3
            if beat in [0, 2]:
                track.append(Message('note_on', note=kick, velocity=80, time=time, channel=channels['percussion']))
                track.append(Message('note_off', note=kick, velocity=0, time=120, channel=channels['percussion']))
                time = 0
            # Snare on beats 2 and 4 with slight velocity variation
            if beat in [1, 3]:
                track.append(Message('note_on', note=snare, velocity=random.randint(60, 90), time=time, channel=channels['percussion']))
                track.append(Message('note_off', note=snare, velocity=0, time=120, channel=channels['percussion']))
                time = 0

            # Add hi-hat offbeat to create swing (e.g. on the "and" of beats)
            if beat < 3:
                # Closed hi-hat on offbeat after each beat
                track.append(Message('note_on', note=closed_hh, velocity=40, time=60, channel=channels['percussion']))
                track.append(Message('note_off', note=closed_hh, velocity=0, time=60, channel=channels['percussion']))
                # Occasionally add open hi-hat for excitement
                if random.random() < 0.15:
                    track.append(Message('note_on', note=open_hh, velocity=50, time=0, channel=channels['percussion']))
                    track.append(Message('note_off', note=open_hh, velocity=0, time=120, channel=channels['percussion']))

def generate_complementary_melody(main_melody):
    complementary = []
    for i, note in enumerate(main_melody):
        if i % 4 == 2:
            new_note = note + 3
        elif i % 4 == 0:
            new_note = note + 5
        else:
            new_note = note
        complementary.append(new_note if new_note in low + middle + high else note)
    return complementary

def add_notes(track, channel, melody, is_main=False):
    durations = swing_durations(len(melody))
    for i, note in enumerate(melody):
        # Higher velocity for main melody and complementary tracks to add energy
        velocity = random.randint(100, 127) if is_main else random.randint(60, 80)
        delay = random.randint(-15, 15)  # Slight humanization
        on_time = max(delay, 0)
        off_time = max(durations[i] - delay, 0)
        # Add slight random start delay except for first note
        track.append(Message('note_on', note=note, velocity=velocity, time=on_time if i == 0 else 0, channel=channel))
        track.append(Message('note_off', note=note, velocity=0, time=off_time, channel=channel))

# Structure
total_bars = 16
notes_per_bar = 8
total_notes = total_bars * notes_per_bar

# Generate main melody with register changes every 6 notes
main_melody = generate_register_changing_melody(total_notes, segment_size=6)

# Generate low and high complementary melodies based on main melody pattern
main_melody_low = [note - 12 if (note - 12) >= 40 else note for note in main_melody]
main_melody_high = [note + 12 if (note + 12) <= 84 else note for note in main_melody]

background_melody = generate_background_melody(main_melody)
second_melody = generate_complementary_melody(main_melody)

# Add notes to tracks
add_notes(main_track, channels['main'], main_melody, is_main=True)
add_notes(main_layer2, channels['main2'], main_melody_low, is_main=True)
add_notes(main_layer3, channels['main3'], main_melody_high, is_main=True)
add_notes(background_track, channels['background'], background_melody)
add_notes(second_melody_track, channels['second'], second_melody, is_main=True)
add_percussion(percussion_track, total_bars)

filename = f"{random.randint(100000,999999)}.mid"
mid.save(filename)
print(f"Saved {filename}")
