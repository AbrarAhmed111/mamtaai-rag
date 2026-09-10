# Oximeter and Vital Signs Monitoring — MumtaAI

## Overview

MumtaAI's Pulse Oximeter feature allows parents to wirelessly connect a compatible Bluetooth pulse oximeter directly through their web browser. You can view your baby's oxygen saturation (SpO2), heart rate (Pulse in BPM), and pulse strength (Perfusion Index) in real time, view live trend charts, and receive smart alerts if readings stay outside safe thresholds.

---

## Supported Devices

MumtaAI connects to standard Bluetooth Low Energy (BLE) pulse oximeters that support direct wireless streaming, including:
- **Creative Medical PC-60F**
- **Creative Medical PC-60FW**
- **Wellue Bluetooth Pulse Oximeters** (O2Ring, BabyO2, and compatible models)
- Other BLE pulse oximeters utilizing standard health telemetry protocols.

---

## Browser and Platform Compatibility

Because MumtaAI connects directly via the modern **Web Bluetooth** standard, browser compatibility is important:

| Platform | Recommended Browser | Bluetooth Supported? | Notes |
|---|---|:---:|---|
| **Android** | Google Chrome, Microsoft Edge | **Yes** | Make sure Bluetooth and Location are enabled on your device. |
| **Windows (10 / 11)** | Google Chrome, Microsoft Edge | **Yes** | Turn Bluetooth ON in Windows Settings. |
| **macOS (MacBook, iMac)** | Google Chrome, Microsoft Edge | **Yes** | Ensure Bluetooth permissions are granted to the browser in System Settings. |
| **Apple iOS (iPhone / iPad)** | Safari, Chrome, Edge | **No** (Direct BLE not supported) | **Apple restriction**: Apple does not support Web Bluetooth in any iOS browser. You can still view live readings logged by another device or caregiver. |

---

## How to Connect Your Pulse Oximeter (Step-by-Step)

1. **Prepare the Device**:
   - Turn on your Bluetooth pulse oximeter.
   - Gently place the sensor on your baby's foot, toe, or hand according to the device manufacturer's instructions.
   - Ensure the device display shows active numbers.
2. **Open MumtaAI**:
   - On a supported device (Android phone or computer using Chrome/Edge), open MumtaAI.
   - Select your baby and navigate to the **Oximeter** tab.
3. **Connect**:
   - Click **Connect Oximeter**.
   - A browser popup window will appear listing nearby Bluetooth devices.
   - Select your oximeter name (e.g., *PC-60F*, *Wellue*, or *Pulse Oximeter*) from the list and click **Pair / Connect**.
4. **Live Monitoring**:
   - The connection indicator turns green: **Connected**.
   - Your baby's live SpO2, pulse rate, and perfusion index will begin updating on your screen every second!

---

## Understanding Your Baby's Vitals

### 1. Oxygen Saturation (SpO2 %)
- Measures the percentage of oxygen carried in your baby's arterial blood.
- **Normal Healthy Baseline**: 95% to 100%.
- **Newborn Consideration**: SpO2 is naturally lower in the immediate newborn period (first minutes to hours after birth) as the lungs transition to breathing room air.
- **Clinical Warning Sign**: Beyond the immediate newborn period, an SpO2 of **<90% to 92%** may suggest an underlying respiratory condition (such as bronchiolitis, pneumonia, or airway obstruction) or cyanotic congenital heart disease. Sustained readings below 90–92% require prompt medical evaluation.

---

### 2. Normal Heart Rate (Pulse Rate in BPM) by Age

Infant and child resting heart rates vary significantly depending on age and whether the child is awake or asleep:

| Age Group | Awake Heart Rate (BPM) | Asleep Heart Rate (BPM) |
|---|:---:|:---:|
| **Neonate (< 28 days)** | **100 – 205 BPM** | **90 – 160 BPM** |
| **Infant (1 – 12 months)** | **100 – 190 BPM** | **90 – 160 BPM** |
| **Toddler (1 – 2 years)** | **98 – 140 BPM** | **80 – 120 BPM** |
| **Preschool (3 – 5 years)** | **80 – 120 BPM** | **65 – 100 BPM** |
| **School-Age (6 – 11 years)** | **75 – 118 BPM** | **58 – 90 BPM** |
| **Adolescent (12 – 15 years)** | **60 – 100 BPM** | **50 – 90 BPM** |

*Note: Heart rate naturally elevates during crying, fever, active kicking, or feedings, and drops to its lowest resting levels during deep sleep.*

---

### 3. Normal Respiratory Rate (Breaths / Minute) by Age

While pulse oximeters measure oxygen saturation and pulse rate, observing your child's breathing rate provides crucial context when assessing overall respiratory comfort:

| Age Group | Normal Respiratory Rate (Breaths / Min) |
|---|:---:|
| **Infant (< 1 year)** | **30 – 53 breaths / min** |
| **Toddler (1 – 2 years)** | **22 – 37 breaths / min** |
| **Preschool (3 – 5 years)** | **20 – 28 breaths / min** |
| **School-Age (6 – 11 years)** | **18 – 25 breaths / min** |
| **Adolescent (12 – 15 years)** | **12 – 20 breaths / min** |

*How to measure: Count chest rises for a full 60 seconds while your child is quiet or resting. A respiratory rate consistently above these ranges (tachypnea), paired with chest retractions or grunting, warrants immediate medical assessment.*

---

### 4. Perfusion Index (PI)
- Measures the strength of the arterial pulse signal at the sensor site (scale: 0.2% to 20%).
- **Good Signal**: A PI above 1.0% indicates a strong, reliable sensor reading.
- **Weak Signal (< 0.5%)**: Often indicates that the sensor is loose, the baby's extremities are cold, or the sensor needs to be repositioned on the foot or toe.

---

## Smart Alerts: How Sustained Threshold Alerting Works

Babies move frequently. When a baby kicks or wriggles, the sensor may temporarily shift for a second, causing an artificial brief drop in readings. 

To protect parents from unnecessary panic caused by false alarms, MumtaAI uses a **Sustained Breach Tracker**:

1. **5-Second Verification**: If a reading drops below your configured threshold (e.g., SpO2 < 90%), MumtaAI watches the reading continuously for **5 full seconds**.
2. **Automatic Reset**: If your baby merely kicked and the reading normalizes within 5 seconds, no alarm sounds.
3. **Gentle Parent Alert**: If the breach continues uninterrupted for more than 5 seconds, an audible chime sounds and an alert banner appears:
   > *"Please check on [Baby's Name] — monitor readings look lower than usual for a few moments. Ensure baby is calm, comfortable, and the sensor is placed snugly. If something does not look right, contact your doctor."*
4. **60-Second Cooldown**: Once alerted, a 60-second cooldown prevents repeated alarm beeping while you are attending to your child.

---

## Customizing Alert Thresholds for Your Baby

1. As the Primary Parent, go to your baby's profile settings and select **Oximeter Alert Thresholds**.
2. Customize the safe parameters:
   - **Low SpO2 Limit**: Default is 90% (adjust between 50% and 100%).
   - **Low Pulse Limit**: Default is 80 BPM (adjust between 30 and 250 BPM).
   - **High Pulse Limit**: Default is 160 BPM (adjust between 30 and 250 BPM).
3. Click **Save Thresholds**.

---

## Important Safety Disclaimers

> [!CAUTION]
> **MumtaAI is NOT a Life-Support or Clinical Medical Monitor**
> 
> 1. **Home Awareness Only**: This feature is intended for parental peace of mind, routine wellness logging, and health awareness. It is **not** an FDA-cleared clinical life-support alarm.
> 2. **Never Rely on Technology Alone**: Always check your baby visually. Look at skin color, breathing comfort, responsiveness, and alertness.
> 3. **No Automatic 911 / Emergency Dispatch**: MumtaAI does **not** notify doctors or emergency responders. If your child appears pale, blue, unresponsive, or struggling to breathe, call emergency services (911 / 112) immediately.

---

## Troubleshooting Oximeter Connections

### 1. The device does not appear in the Bluetooth list
- Make sure the oximeter is turned on and within 2–3 meters (6–10 feet) of your computer or phone.
- If previously paired with another phone or manufacturer app, disconnect it there first (Bluetooth devices can usually only connect to one app at a time).
- On Android, ensure **Location** and **Bluetooth** are turned on in system settings.

### 2. Connection drops frequently
- Keep your phone or laptop in the same room as your baby.
- Check the oximeter's battery level. Low batteries often cause Bluetooth drops.
- MumtaAI automatically attempts to reconnect up to 5 times if a connection drops.

### 3. SpO2 displays "--" or reads zero
- The sensor is not picking up a clear pulse. Check that the probe is snugly fitted against the skin and the baby's foot/hand is warm.
