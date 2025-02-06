import numpy as np
import matplotlib.pyplot as plt

# Reference IRE levels
ire_levels = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])

# Equivalent mV values for the IRE levels
reference_mv_values = np.array([0, 70, 140, 210, 280, 350, 420, 490, 560, 630, 700])

# DAC measurements (mV)
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

# Calculate median and standard deviation
median = np.median(dac_measurements, axis=0)
std_dev = np.std(dac_measurements, axis=0)

# Identify outliers (e.g., values that are more than 0.25 standard deviations from the median)
threshold = 0.25
outliers = np.abs(dac_measurements - median) > threshold * std_dev

# Filter out the outliers
filtered_measurements = np.where(outliers, np.nan, dac_measurements)

# Truncate and round the filtered data for simpler viewing, removing nan values
truncated_filtered_measurements = [
    [int(val) if not np.isnan(val) else None for val in row]
    for row in filtered_measurements.T
]

# Calculate the correction curve
correction_curve = median + (reference_mv_values - median) * 2

# Define hdmi_limited_2_coeffs as a numpy array
hdmi_limited_2_coeffs = np.array([
    [0.93701171875, 0.0, 0.0, 0.06250],
    [0.0, 0.93701171875, 0.0, 0.06250],
    [0.0, 0.0, 0.93701171875, 0.06250],
    [0.0, 0.0, 0.0, 1.0]
])

# Define hdmi_limited_2 curve equivalent mV values
hdmi_limited_2_coeffs_mv = hdmi_limited_2_coeffs[0, 0] * reference_mv_values + hdmi_limited_2_coeffs[0, 3] * 700

# Calculate the error curve as the difference between the reference line and the correction curve
error_curve = correction_curve - reference_mv_values
error_curve_HDMI2 = correction_curve - hdmi_limited_2_coeffs_mv
HDMI2offset_correction_curve = reference_mv_values - error_curve_HDMI2

# Plotting the original plot with error curve
plt.figure(figsize=(14, 8))

plt.subplot(1, 2, 1)
plt.plot(ire_levels, reference_mv_values, label='Reference IRE Levels', color='green', linewidth=2)
plt.plot(ire_levels, median, label='Median DAC Measurements', color='blue', linewidth=2)
plt.plot(ire_levels, correction_curve, label='Correction Curve', color='red', linestyle='--', linewidth=2)
plt.fill_between(ire_levels, correction_curve - std_dev, correction_curve + std_dev, color='red', alpha=0.3, label='Standard Deviation around Correction Curve')
plt.plot(ire_levels, hdmi_limited_2_coeffs_mv, label='HDMI Limited 2 Coeffs', color='purple', linestyle='-.', linewidth=2)
plt.plot(ire_levels, error_curve, label='Error Curve (Reference - Correction)', color='orange', linestyle=':', linewidth=2)

plt.xlabel('IRE Level')
plt.ylabel('mV Value')
plt.title('Original Plot with Error Curve')
plt.legend(loc='upper left')
plt.grid(True)

# Plotting the secondary plot
plt.subplot(1, 2, 2)
plt.plot(ire_levels, hdmi_limited_2_coeffs_mv, label='HDMI Limited 2 Coeffs', color='purple', linestyle='-.', linewidth=2)
plt.plot(ire_levels, correction_curve, label='Original Correction Curve', color='red', linestyle='--', linewidth=2)
plt.plot(ire_levels, error_curve_HDMI2, label='Error Curve (Correction - HDMI2)', color='orange', linestyle=':', linewidth=2)
plt.plot(ire_levels, HDMI2offset_correction_curve, label='HDMI2 correction (HDMI2 - Correction)', color='blue', linestyle=':', linewidth=2)

plt.xlabel('IRE Level')
plt.ylabel('mV Value')
plt.title('Secondary Plot: HDMI Limited 2 Active')
plt.legend(loc='upper left')
plt.grid(True)

plt.tight_layout()
plt.show()

# Convert HDMI2offset_correction_curve to 8-bit gamma range and print the values
HDMI2_Gamma_correction_curve = np.interp(HDMI2offset_correction_curve, (HDMI2offset_correction_curve.min(), HDMI2offset_correction_curve.max()), (0, 255))
print("HDMI-Gamma-correction_curve = np.array([{}])".format(', '.join(map(str, HDMI2_Gamma_correction_curve.astype(np.int32)))))