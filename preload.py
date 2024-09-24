import os
os.environ['NUMBA_DISABLE_JIT'] = '1'

import numpy as np
import librosa
import numba

# Force librosa to use numpy instead of numba
librosa.util.utils._localmax = lambda x: np.logical_and.reduce([x > np.roll(x, 1), x >= np.roll(x, -1)])