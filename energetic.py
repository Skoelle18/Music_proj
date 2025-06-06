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

# Energetic tempo
bpm = 120
tempo = mido.bpm2tempo(bpm)
for track in mid.tracks:
    track.append(MetaMessage('set_tempo', tempo=tempo))

# Brighter, energetic instruments
main_instruments = {'distortion_guitar': 30, 'overdriven_guitar': 29, 'rock_organ': 19, 'synth_bass': 38}
background_instruments = {'lead_2_sawtooth': 81, 'lead_1_square': 80, 'synth_brass': 63}
percussion_instruments = {'kick': 36, 'snare': 38, 'closed_hh': 42, 'open_hh': 46}

main_instr_name, main_instr_prog = random.choice(list(main_instruments.items()))
background_instr_name, background_instr_prog = random.choice(list(background_instruments.items()))
percussion_channel = 9
print(f"Main instrument: {main_instr_name}")
print(f"Background instrument: {background_instr_name}")

channels = {'main': 0, 'main2': 1, 'main3': 2, 'background': 3, 'percussion': percussion_channel, 'second': 4}

# Program changes
main_track.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main']))
# main_layer2.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main2']))
# main_layer3.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['main3']))
background_track.append(Message('program_change', program=background_instr_prog, time=0, channel=channels['background']))
second_melody_track.append(Message('program_change', program=main_instr_prog, time=0, channel=channels['second']))

# Dorian scale for funky energy
dorian_scale = [60, 62, 63, 65, 67, 69, 70, 72]  # C D Eb F G A Bb C
high = [note + 12 for note in dorian_scale]
middle = dorian_scale
low = [note - 12 for note in dorian_scale]
registers = [low, middle, high]

def swing_durations(num_notes):
    return [240 if i % 2 == 0 else 120 for i in range(num_notes)]

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
                possible_notes = [n for n in current_register if abs(n - prev_note) <= 7]
                note = random.choice(possible_notes) if possible_notes else random.choice(current_register)

            if random.random() < 0.2 and len(melody) > 0:
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
        velocity = random.randint(110, 127) if is_main else random.randint(80, 100)
        delay = random.randint(-10, 10)
        on_time = max(delay, 0)
        off_time = max(durations[i] - delay, 0)
        track.append(Message('note_on', note=note, velocity=velocity, time=on_time if i == 0 else 0, channel=channel))
        track.append(Message('note_off', note=note, velocity=0, time=off_time, channel=channel))

def add_percussion(track, bars=16):
    kick, snare, closed_hh, open_hh = percussion_instruments['kick'], percussion_instruments['snare'], percussion_instruments['closed_hh'], percussion_instruments['open_hh']
    ticks = 480
    for bar in range(bars):
        for beat in range(4):
            time = ticks if not (bar == 0 and beat == 0) else 0

            if beat in [0, 2]:  # Kick
                track.append(Message('note_on', note=kick, velocity=90, time=time, channel=channels['percussion']))
                track.append(Message('note_off', note=kick, velocity=0, time=100, channel=channels['percussion']))
                time = 0
            if beat in [1, 3]:  # Snare
                track.append(Message('note_on', note=snare, velocity=random.randint(90, 110), time=time, channel=channels['percussion']))
                track.append(Message('note_off', note=snare, velocity=0, time=100, channel=channels['percussion']))
                time = 0

            if beat < 3:
                track.append(Message('note_on', note=closed_hh, velocity=60, time=30, channel=channels['percussion']))
                track.append(Message('note_off', note=closed_hh, velocity=0, time=30, channel=channels['percussion']))
                if random.random() < 0.2:
                    track.append(Message('note_on', note=open_hh, velocity=60, time=0, channel=channels['percussion']))
                    track.append(Message('note_off', note=open_hh, velocity=0, time=100, channel=channels['percussion']))

# Structure
total_bars = 16
notes_per_bar = 8
total_notes = total_bars * notes_per_bar

main_melody = generate_register_changing_melody(total_notes, segment_size=6)
main_melody_low = [note - 12 if (note - 12) >= 40 else note for note in main_melody]
main_melody_high = [note + 12 if (note + 12) <= 84 else note for note in main_melody]
background_melody = generate_background_melody(main_melody)
second_melody = generate_complementary_melody(main_melody)

# Add to tracks
add_notes(main_track, channels['main'], main_melody, is_main=True)
add_notes(main_layer2, channels['main2'], main_melody_low, is_main=True)
add_notes(main_layer3, channels['main3'], main_melody_high, is_main=True)
add_notes(background_track, channels['background'], background_melody)
add_notes(second_melody_track, channels['second'], second_melody, is_main=True)
add_percussion(percussion_track, 6)

# Save
filename = f"energetic_{random.randint(100000,999999)}.mid"
mid.save(filename)
print(f"Saved {filename}")