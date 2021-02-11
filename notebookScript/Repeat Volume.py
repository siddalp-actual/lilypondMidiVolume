# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.9.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Increasing Midi Volume on each iteration
#
# Hymns, Psalms etc are typically written in Lilypond as a `\repeat volta n` construct.  It would be useful to be able to increase the volume each time through.  How can I do that?
#
# ## Idea 1
#
#  1) The manual shows how to override the dynamic volume function for a particular dynamic mark.
# ```
# #(define (myDynamics dynamic)
#     (if (equal? dynamic "rfz")
#       0.9
#       (default-dynamic-absolute-volume dynamic)))  
# ```
# ```
# \score {
#   \new Staff {
#     \set Staff.midiInstrument = #"cello"
#     \set Score.dynamicAbsoluteVolumeFunction = #myDynamics
#     \new Voice {
#       \relative c'' {
#         a4\pp b c-\rfz
# ```
#
#  1) If I define my own dynamic mark and put it on the first (or last) note in the repeated section, maybe I can use it for a fractional increase in volume.  
# A new dynamic mark can be created with
# ```
#  sfzp = #(make-dynamic-script "sfzp")
# ¬¬¬
#
#  1) But I need to be able to get hold of the current value of the volume.  What or Where is that?

# %% [markdown]
# > I found the lilypond source at `/usr/share/lilypond/2.20.0/scm/midi.scm`
#
# This shows that dynamic-default-volume is set to 0.71 = 90/127 (we can see the 90's in the midi dump below)  
#
# ../ly/performer-init.ly sets the default Score context to have a property `dynamicAbsoluteVolumeFunction = #default-dynamic-absolute-volume`
# which is defined in ../scm/midi.scm
#
# Setting the midi performer minimum volume to 0.8 results in velocity 119/127 = 0.93

# %% [markdown]
# ### Aside - dumping midi files with mido
#
# The Python package, mido, can be used for creating or parsing midi files.  The following code prints out the `.ly` file and then dumps the `.midi` file created from it.  The first couple of columns give the offset in midi-ticks and seconds of the formatted event.

# %%
import mido
import datetime
import subprocess

#file_stem = "./dynamicPart"
file_stem = "../repeatStave"

file_source = file_stem + ".ly"
file_midi = file_stem + ".midi"
file_contents = subprocess.run(['cat', file_source], capture_output=True, text=True)
print(file_contents.stdout) #.decode('unicode_escape'))

midi_data = mido.MidiFile(file_midi)
display(midi_data)
display(midi_data.length,"seconds?")
print(midi_data.ticks_per_beat)

for i, midi_track in enumerate(midi_data.tracks):
    display(f"Track: {i}")
    display(midi_track)
    time_seq = 0
    for msg in midi_track:
        time_seq += msg.time
        t_s = datetime.timedelta(seconds=mido.tick2second(time_seq, ticks_per_beat = midi_data.ticks_per_beat, tempo = 500000))
        display(f"{time_seq:05d} = {t_s.total_seconds(): 3.2f} : {msg}")

# %% [markdown]
# ## So Where can I find the midi volume (or velocity)
#
# Looking at the Lilypond side with \displayMusic I see things such as:
# ```
#            (list (make-music
#                     'NoteEvent
#                     'articulations
#                     (list (make-music
#                             'CrescendoEvent
#                             'span-direction
#                             -1))
#                     'duration
#                     (ly:make-duration 2)
#                     'pitch
#                     (ly:make-pitch -1 0))
#                   (make-music
#                     'NoteEvent
#                     'duration
#                     (ly:make-duration 2)
#                     'pitch
#                     (ly:make-pitch -1 1))
#                   (make-music
#                     'NoteEvent
#                     'articulations
#                     (list (make-music
#                             'AbsoluteDynamicEvent
#                             'text
#                             "ff"))
# ```
# for a `\cr` and `\ff` markup of the music.  Suggesting it must be the "midi-performer" code which is translating this into note velocities.
#
# > search the code for AbsoluteDynamicEvent

# %% [markdown]
# ## Something that works
#
#  1) define a `register` function which uses a scheme closure to encapsulate a value and some methods on it
# ```
# myReg =
# #(define-scheme-function (parser location init-val)
#     (number?)
#     ;; init-val is explicitly frozen in the local let environment
#     (let ((regVal init-val))
#         (define (get-val)
#             regVal)  ;; return the current value
#         (define (set-val amount)
#             (set! regVal amount)
#             regVal)  ;; return the set value
#         (define (up-val)
#             (set! regVal (* 4 (get-val)))
#             regVal)  ;; return the new value
#
#         ;; think of this as constructor which binds the methods to the state
#         (lambda args
#             (apply
#                 (case (car args)
#                     ;; get-value is frozen as its value in the lambda
#                     ((get-value) get-val)
#                     ((set-value) set-val)
#                     ((up-value) up-val)
#                     (else (error "Invalid method!")))
#                 (cdr args)
#             )
#         )
#     )
# )
# ```
#   1) set up volume to be an instance of this register function
# ```
# #(define volume (myReg 0.8))  % 0.8 * 127 = 102
# ```
#  
#  1) set up \rfz dynamic to use the `(volume 'get-value)`
# ```
# #(define (myDynamics dynamic)
#     (if (equal? dynamic "rfz")
#         (volume 'get-value)
#         (default-dynamic-absolute-volume dynamic)
#     )
# )
# ``` 
#  1) Override the volume function for the score so that it picks up the `myDynamics` function.
#  ```
#      \set Score.dynamicAbsoluteVolumeFunction = #myDynamics
# ```

# %% [markdown]
# ## Example
#
# An working example of this technique can be found in `dynamicPart.ly`.  The functions in the example follow this technique, but have been enhanced.
#
# Should it be necessary to reset the volume or the increment, this can be done using lilypond instructions of the form:
# ```
# #(volume 'set-value 0.8)  % 0.8 * 127 = 102
# ```

# %%
