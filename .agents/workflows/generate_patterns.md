---
description: How to generate and load cycling patterns for the signal generator
---

# Generating and Loading Cycling Patterns

This workflow guides you through creating custom arbitrary waveform (.arb) patterns and loading them into the signal generator for continuous cycling tests.

## 1. Open the Pattern Generator
1. Run the main application: `python main.py`
2. Click the **Pattern Generator** button in the main menu.

## 2. Define Waveform Parameters
Enter the desired electrical and timing parameters in the "Waveform Parameters" frame:
- **Pulse Width (µs):** Duration of the active pulse.
- **Duty Cycle (%):** Ratio of pulse width to total period.
- **Number of Pulses:** Total pulses in the sequence before the ramp.
- **Amplitude Top/Bottom (V):** Voltage levels for the pulse sequence.
- **Ramp Width (µs):** Duration of the ascent/descent ramp.
- **Amplitude Ramp (V):** Peak voltage for the ramp portion.

## 3. Preview and Verify
- Click **Preview Plot** to visualize the generated waveform on the embedded canvas.
- Ensure the pulse sequence and ramps match your test requirements.

## 4. Export the Pattern Files
1. Click **Export to .arb**.
2. Select a destination folder in the file dialog.
3. The tool will generate two files:
   - `[Name].arb`: The raw arbitrary waveform data.
   - `[Name]_filtered.arb`: A smoothed version of the waveform using a Hanning window filter to reduce high-frequency ringing.

## 5. Load into Signal Generator
1. Go to the **Cycling Test** tab in the main application.
2. Use the directory browser to select the folder where you exported the `.arb` files.
3. Select the generated pattern from the list and load it into the connected signal generator.
