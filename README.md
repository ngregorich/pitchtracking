# pitchtracking

A proof of concept of *pitch tracking* a musical instrument using autocorrelation in Python

## Background

Pitch tracking determines the note played by the musician in an audio sample and can be used to control synthesizers or in the well known *autotune* algorithms.

Simpler algorithms can use amplification and filtering  followed by zero crossing detection, but this technique can have shortcomings on complex waveforms.

One of the more difficult musical sounds to track is the open low E string in a bass guitar, which has a fundamental frequency of 41.2 Hz. This tracking this low frequency adds latency to a system and the harmonic structure introduces difficulty in determining which octave the note was played in

## Goals

The goal is to be able to feed the algorithm audio samples of single (*no simultaneous*) notes being played on bass guitar and plotting the tracked frequency over time. This should include open low E, E an octave up, and various other notes.

In order to achieve this goal, a simpler test case was created. A generated sine wave with a frequency of 41.2 Hz and a duration of approximately 5 seconds was created. This known test vector will allow algorithm development without the complexity of harmonics. After the initial algorithm development, the input can be switched to actual bass guitar samples.

## Methodology

The first step was to generate an approximately 5 second audio sample of a 41.2 Hz sine wave. I believe the audio editing tool Audacity was used to create this sample, but it could also be done in Python. This file is called *41_mono_48k.wav*. The first 100 ms looks like:

![generated first 100 ms](https://raw.githubusercontent.com/ngregorich/pitchtracking/master/generated_first_100_ms.png)

*Algorithm details omitted, take a look at pitch.py which is well commented*

The resulting frequency tracking of the generated sine wave looks as expected:

![generated tracking](https://raw.githubusercontent.com/ngregorich/pitchtracking/master/generated_actual_frequency.png)

The solid red line is the actual frequency of the generated sine wave, 41.2 Hz (open low E). The dotted red line is one semitone higher than open low E and has a frequency of 43.65 Hz. Finally, the blue line is the frequency tracked by the autocorrelation algorithm.

Notice how the blue line oscillates about the known frequency. Indeed, we have tracked the generated sine wave's frequency with no apriori knowledge (note: we would likely get similar results by counting zero crossing, which whould be a worthwhile comparison)! The glitch near 5 seconds is likely when the input audio is finished, leaving the algorithm with no input signal to track.

Next, an open low E sample was loaded into the algorithm. The first 100 ms look like:

![bass first 100 ms](https://raw.githubusercontent.com/ngregorich/pitchtracking/master/bass_first_100_ms.png)

As you can see, the waveform is more complex, it has harmonics! You also may imagine that a zero crossing counter would be in some trouble with this sample.

Running the autocorrelation algorithm on the actual bass sample did not yield the expected, or at least hoped for, results:

![bass tracking](https://raw.githubusercontent.com/ngregorich/pitchtracking/master/bass_actual_frequency.png)

Notice there isn't much but a couple of glitches in the 41.2 Hz frequency band we know the open low E should be in. The algorithm is attempting to call the harmonic with the highest amplitude the root note. As we have found, this does not always correlate to the root note being played.

Various white papers have been written on determining the true root note. For demonstration purposes, we can do some hand waving to see what the results would look like if things went according to plan.

Note: the autocorrelation algorithm as implemented is looking for several peak frequencies, not just 1. Since 41.2 Hz always happens to be in the top 4 highest amplitude frequencies tracked, we can plot the frequency in this range for every run of the autocorrelation:

![bass tracking](https://raw.githubusercontent.com/ngregorich/pitchtracking/master/bass_frequency_40_to_42_hz.png)

Wow, it worked! The first thing we can say is that this bass guitar may be out of tune, based on the offset between the blue tracked bass line and the solid red low open E line. We also see a small peak in frequency at the beginning of the sample when the string is plucked and a graduate decrease in frequency as the string loses energy over time. At the very end of the note being played, we see oscillation and / or noise added to the tracked signal. This also seems as expected, as the string loses energy it is easy to imagine its oscillation as becoming more chaotic or less stable.

## Conclusion

Python is a great language to prototype a signal processing algorithm like an autocorrelation based pitch tracker. It provides packages to read actual .wav files, perform correlation (autocorrelation if you feed both inputs the same signal), and of course matplotlib plotting.

The algorithm itself also looks promising. It works like a charm on simple input waveforms and has shown potential to track more complex waveforms, provided their harmonic structure is *decoded*.