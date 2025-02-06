import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# Reference levels 
ire_levels = np.linspace(0, 100, 11)
reference_mv_values = np.linspace(0, 700, 11)
reference_curve = (reference_mv_values / 700) * 255  # (8-bit values)

# HDMI limited 2 coefficients from mister.ini 
hdmi_limited_2_coeffs = np.array([0.93701171875, 0.06250])
hdmi_limited_2_coeffs_mv = hdmi_limited_2_coeffs[0] * reference_mv_values + hdmi_limited_2_coeffs[1] * 700
hdmi_2_curve = (hdmi_limited_2_coeffs_mv / 700) * 255  # 

# DAC measurements for correction curve
dac_measurements = np.array([
    [0, 24, 98, 170, 248, 344, 414, 486, 562, 632, 700],
    [0, 24, 100, 172, 246, 344, 416, 490, 564, 636, 706],
    [0, 24, 100, 178, 254, 356, 428, 504, 578, 654, 728],
    [0, 24, 98, 170, 248, 344, 414, 486, 562, 632, 700],
    [0, 24, 100, 172, 246, 344, 416, 490, 564, 636, 706],
    [0, 24, 94, 166, 234, 328, 394, 464, 532, 604, 668],
    [0, 26, 98, 170, 244, 338, 408, 480, 552, 624, 694],
    [0, 24, 100, 178, 254, 356, 428, 504, 578, 654, 728],
    [0, 26, 104, 182, 254, 356, 428, 502, 578, 652, 724],
    [0, 26, 98, 168, 242, 332, 402, 474, 546, 616, 684],
    [0, 26, 104, 176, 252, 350, 420, 496, 566, 642, 712],
    [0, 32, 106, 176, 248, 344, 412, 482, 552, 624, 694],
    [0, 34, 112, 192, 268, 374, 450, 528, 606, 684, 752],
    [0, 74, 144, 216, 286, 384, 450, 522, 594, 660, 726],
    [0, 72, 144, 216, 286, 380, 446, 518, 586, 656, 720]
])
correction_curve = (reference_mv_values * 2) - np.median(dac_measurements, axis=0)
original_correction_curve = (correction_curve / 700) * 255  

# Calculate updated correction curve
updated_correction_curve = (original_correction_curve - hdmi_2_curve) + reference_curve
updated_correction_curve = np.clip(updated_correction_curve, 0, 255)  
full_range = np.arange(256)
linear_interpolated_curve = interp1d(np.linspace(0, 255, len(updated_correction_curve)), updated_correction_curve, kind='linear', fill_value="extrapolate")(full_range)
cubic_interpolated_curve = interp1d(np.linspace(0, 255, len(updated_correction_curve)), updated_correction_curve, kind='cubic', fill_value="extrapolate")(full_range)

# Apply tweaks
# Uncomment the following lines to apply specific tweaks
# tweak_values = [0, -10, 0, 0, 0, 5, 0]  # Shadow increase tweak
# tweak_values = [5, 10, 15, 20, 25, 30, 35]  # Brightness increase tweak
# tweak_values = [-20, -15, -10, -5, 0, 5, 10]  # Shift Black and White Points
# tweak_values = [-20, -15, -10, -5, 0, 0, 0]  # Shift Black Point
# tweak_values = [2, 4, 6, 8, 6, 4, 2]  # Mild Gamma Boost
# tweak_values = [5, 10, 15, 20, 15, 10, 5]  # Moderate Gamma Boost
tweak_values = [+1, -4, -6, -10, -6, -4, +1]  # Mild Gamma Reduction
# tweak_values = [-5, -10, -15, -20, -15, -10, -5]  # Moderate Gamma Reduction
# tweak_values = [0, -10, 0, 0, 0, 10, 0]  # Sigmoid Gamma Curve
# tweak_values = [0, 0, 0, 0, 0, 0, 0]  # Default tweak values (no change)

# Interpolate the tweak values to match the full range
tweak_curve = interp1d(np.linspace(0, 255, len(tweak_values)), tweak_values, kind='cubic', fill_value="extrapolate")(full_range)
tweaked_curve = np.clip(cubic_interpolated_curve + tweak_curve, 0, 255)

def save_curve(filename, description, curve):
    with open(filename, "w") as f:
        f.write(f"# {description}\n")
        for value in curve:
            print(value)
            f.write(f"{value}\n")

save_curve("linear_interp.txt", "HDMI2 Correction curve with linear interpolation", np.round(linear_interpolated_curve).astype(np.int32))
save_curve("cubic_interp.txt", "HDMI2 Correction curve with cubic interpolation", np.round(cubic_interpolated_curve).astype(np.int32))
save_curve("tweaked_curve.txt", "HDMI2 Correction curve with tweaked gamma", np.round(tweaked_curve).astype(np.int32))

plt.figure(figsize=(14, 8))

plt.subplot(1, 2, 1)
plt.plot(np.linspace(0, 255, len(reference_curve)), reference_curve, label='Reference Curve (8-bit)', color='green', linestyle='-', linewidth=2)
plt.plot(np.linspace(0, 255, len(hdmi_2_curve)), hdmi_2_curve, label='HDMI_2 Curve (8-bit)', color='purple', linestyle='-.', linewidth=2)
plt.plot(np.linspace(0, 255, len(original_correction_curve)), original_correction_curve, label='Original Correction Curve (8-bit)', color='blue', linestyle='--', linewidth=2)
plt.xlabel('IRE Level (0-255)')
plt.ylabel('8-bit Value')
plt.title('Curves (0-255 Range)')
plt.legend(loc='upper left')
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(full_range, linear_interpolated_curve, label='Linear Interpolation', color='red', linestyle='-', linewidth=2)
plt.plot(full_range, cubic_interpolated_curve, label='Cubic Interpolation', color='blue', linestyle='-', linewidth=2)
plt.plot(full_range, tweaked_curve, label='Tweaked Curve', color='orange', linestyle='-', linewidth=2)
plt.xlabel('IRE Level (0-255)')
plt.ylabel('8-bit Value')
plt.title('Updated Correction Curves (Interpolated)')
plt.legend(loc='upper left')
plt.grid(True)

plt.tight_layout()
plt.show()
