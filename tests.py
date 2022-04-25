import analyzer as an
import numpy as np
import matplotlib.pyplot as plt

t = np.linspace(0, 1, 44100, False)  # 1 second
sig = np.sin(2*np.pi*8e3*t) + np.sin(2*np.pi*15e3*t)
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
ax1.plot(t, sig)
ax1.set_title('8 kHz and 15 kHz sinusoids')
ax1.axis([0, 1e-3, -2, 2])

filtered = an.signal_filtrating(sig, 20, 10e3)
ax2.plot(t, filtered)
ax2.set_title('After [20, 10e3] Hz bandpass filter')
ax2.axis([0, 1e-3, -2, 2])
ax2.set_xlabel('Time [seconds]')
plt.tight_layout()
plt.show()