#%%
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as sio
import collections
import decimal

# bass pluck
# wav_fname = 'long001.wav'
# generated 41.2 Hz wave
wav_fname = '41_mono_48k.wav'

print('done')

#%%

# read wave f0ile
samplerate, data = sio.read(wav_fname)
sampleduration = data.shape[0] / samplerate

print('samplerate = {} samples/s'.format(samplerate))
print('duration = {} s'.format(sampleduration))

try:
    print('number of channels = {}'.format(data.shape[1]))
except:
    if len(data) > 0:
        print('number of channels = 1')
        data = data.astype(float)
    else:
        print('error reading wave')

print('done')

# %%

# plot first 100 ms of wave
time = np.linspace(0., sampleduration, data.shape[0])

fig = plt.figure()
plt.plot(time, data[:,], label="audio in")
plt.grid()
plt.title('Audio In')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.xlim(0, 0.1)
plt.legend()
plt.show()
fig.savefig('first_100_ms.png')

print('done')

# %%

# do autocorrelation and frequency peak detection

run_list = []
Tone = collections.namedtuple('Tone', ['bin', 'frequency', 'amplitude'], verbose=False, rename=False)

# autocorrelation size in points
num_points = 8192
# step size, how many samples to jump for next autocorrelation (overlap)
# more overlap will have quicker response at computational expense
step = 441
# starting samples for each autocorrelation
start_list = range(0, len(data)-2*step, step)

# for each starting sample
for start in start_list:
    # holder for frequency detected
    freq_list = []
    # perform autocorreletion (same data to both inputs of correlation)
    acorr_out = np.correlate(data[start:start+num_points-1,], data[start:start+num_points-1,], 'same')
    # take points 4095 to 8190, unclear why not 4096 to 8191
    acorr_top = acorr_out[num_points//2-1: num_points-2]

    # plot each autocorrelation. there are many. this is a slow operation
    # plt.plot(20*np.log10(np.abs(acorr_top)))
    # plt.xlim(0, num_points//2-1)
    # plt.show()

    # if there appears to be autocorrelation datat
    if len(acorr_top) > 0:
        # print DC bin. no delay, signal compared with itself. this should be maximum output value
        print('y({:7.2f}) = {:.0f} @ {:7.2f} Hz'.format(0.0, 20*np.log10(acorr_top[0]), 0.0))

        # peak detection
        # inititalize last bin to DC
        last = acorr_top[0]
        # initialize previous direction to decreasing
        last_dir = '-'

        i = 0
        # across each bin in the autocorrelation output
        for bin in acorr_top:
            # store to dir whether autocorrelation bin is increasing or decreasing
            if bin - last > 0:
                dir = '+'
            else:
                dir = '-'
            # if was increasing but now decreasing, we have peaked
            if dir == '-' and last_dir == '+':
                # if the new peak is within magic number 6 dB of DC bin, save and print the bin
                if 20*np.log10(acorr_top[i]) > 20*np.log10(acorr_top[0]) - 6:
                    # print('bin {} = {:.0f}, {}'.format(i, 20*np.log10(bin), dir))
                    # last bin was actually peak so go back 1
                    i -= 1
                    # calculate precise frequency between the bins using below p equation
                    # iirc this uses a parabola peak finding equation that should be documented here
                    # load a with previous bin, b with peak bin, and c with next bin
                    a = acorr_top[i-1]
                    b = acorr_top[i]
                    c = acorr_top[i+1]
                    # calculate true peak on x or frequency axis
                    p = 0.5 * (a - c)/(a-2*b+c)
                    # caclulate the true peak's amplitude or y axis in dB
                    y = 20 * np.log10(b - 0.25 * (a - c)*p)
                    # print fractional peak bin, amplitude, and peak frequency detected
                    print('y({:7.2f}) = {:.0f} @ {:7.2f} Hz'.format(i+p, y, samplerate/(i+p)))
                    # store this peak bin to running list
                    freq_list.append(Tone(bin=i+p, frequency=samplerate/(i+p), amplitude=y))
                    # should i be incremented here to return it to its previous value?
            # increment bin pointer
            i += 1
            # store previous bin
            last = bin
            # store previous direction
            last_dir = dir
    # this list stores all detected peaks from each autocorrelation run
    # so it contains the peaks over time
    run_list.append(freq_list)

print('done')

# %%

# print each autocorrelation run bin peak fractional bin and frequency
# plot the frequencies across autocorrelation runs

# float range generator
def float_range(start, stop, step):
  while start < stop:
    yield float(start)
    start += decimal.Decimal(step)

note_list = []
# storage for each autocorrelation run's max amplitude
max_amp = 0
# for each autocorrelation run
for run in run_list:
    # for each peak detected within the run
    for tone in run:
        # find and store peak amplitude and frequency
        if tone.amplitude > max_amp:
            max_amp = tone.amplitude
            max_f = tone.frequency
    # print each autocorrelation run's peak fractional bin and frequency
    print('{:6.2f} @ {:8.2f} Hz'.format(max_amp, max_f))
    # store each max frequency 
    note_list.append((max_f))
    max_amp = 0

# create list of time in seconds for each autocorrelation iteration / step
t = list(float_range(0, sampleduration, step/samplerate))

while len(t) > len(note_list):
    print('this')
    t = t[:-1]

# plot peak frequency detected across each autocorrelation over time
# red line at bass open e note, 41.2 Hz
# red dashed line at one semitone higher, 43.65
fig = plt.figure()
plt.plot(t, note_list)
plt.axhline(y=43.65, color='red', linestyle=':')
plt.axhline(y=41.2, color='red', linestyle='-')
plt.grid()
plt.ylim(40,45)
plt.title('Peak Frequency Over Time')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.show()
fig.savefig('actual_frequency.png')

print('done')

#%%

# since we know the input sample is an open e bass pluck
# we can plot only data points in the known frequncy band
# between 40 and 42 Hz to generate a desired output

i = 0
t = []
note_list = []
for run in run_list:
    for tone in run:
        if tone.frequency > 40.0 and tone.frequency < 42.0:
            # print(tone.frequency)
            t.append(i*step/samplerate/10)
            note_list.append((tone.frequency))
        i += 1

fig = plt.figure()
plt.plot(t, note_list)
plt.axhline(y=43.65, color='red', linestyle=':')
plt.axhline(y=41.2, color='red', linestyle='-')
plt.grid()
plt.ylim(40,45)
plt.title('Tracking in 40-42 Hz Band')
plt.xlabel('Autocorrelation Iteration')
plt.ylabel('Frequency (Hz)')
plt.show()
fig.savefig('frequency_40_to_42_hz.png')

# %%

# attempt add logic to actually generate last plot without fudging

amp_list = [1713494190.6409786,
            1620308588.7240372,
            1495631039.5623,
            1514782084.412035,
            1434749456.414332,
            1388050084.3200018
            ]
freq_list = [166.31,
            83.09,
            55.34,
            41.51,
            33.21,
            27.68
]

sorted_amp = []
sorted_f = []

max_amp = 0
for j in range(len(amp_list)):
    for i in range(len(amp_list)):
        if amp_list[i] > max_amp:
            max_amp = amp_list[i]
            max_i = i
            max_f = freq_list[i]
    sorted_amp.append(amp_list.pop(max_i))
    sorted_f.append(freq_list.pop(max_i))
    max_amp = 0

for i in range(len(sorted_amp)):
    print('{:10.0f} @ {:8.2f} Hz'.format(sorted_amp[i], sorted_f[i]))

for i in range(6):
    ratio = int(np.floor(sorted_f[0]/sorted_f[i]))
    print('{:8.2f}{:5} '.format(sorted_f[i], ratio), end = '')
    for j in range(2, ratio+1):
        print('{:8.2f} '.format(j*sorted_f[i]), end = '')
    print('')
    # print('{:5.2f} {:8.2f}'.format(ratio, sorted_f[0]/(i+1)))

print('done')    
