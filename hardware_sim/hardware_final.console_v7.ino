/*
  Hardware-in-the-Loop Prototype v7: Thermal, Engagement-Zone, and Predictive Additions
  High Altitude Anti-Drone System Simulation (SIH Problem Statement 26050)

  Adds three capabilities to v6, all implemented in software using the
  EXISTING wiring (no new components, no new pins needed):

  1. Thermal management indication - LCD shows "HEATER: ON" when simulated
     temperature drops below a cold threshold, representing a real system's
     anti-icing/heater response (the heater itself is not modeled in
     hardware - this is a status indication of when one would activate).

  2. Neutralization-armed trigger - a distinct buzzer tone (1500Hz, steady,
     not blinking) sounds when the target is within a simulated "engagement
     zone" (close range) AND the system is tracking accurately. This
     represents the response-chain trigger point (detect -> track -> arm),
     NOT an actual neutralization mechanism - no countermeasure hardware
     exists in this circuit.

  3. Predictive trend detection - tracks the last several pointing-error
     readings; if the trend is consistently worsening, the LCD shows
     "TREND WARN" before the error actually crosses the reactive alert
     threshold. This is a simple linear-trend check, not a learned model.

  Pin map is UNCHANGED from v6 - see that file's header comment.
  Libraries needed: Servo, Wire, LiquidCrystal_I2C (unchanged from v6)
*/

#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

Servo panServo;
Servo tiltServo;
LiquidCrystal_I2C lcd(0x27, 16, 2);

const int WIND_POT_PIN     = A0;
const int TEMP_POT_PIN     = A1;
const int MANUAL_PAN_PIN   = A2;
const int MANUAL_TILT_PIN  = A3;
const int MODE_BUTTON_PIN  = 2;
const int TRIG_PIN         = 3;
const int ECHO_PIN         = 4;
const int PAN_SERVO_PIN    = 9;
const int TILT_SERVO_PIN   = 6;
const int LED_GREEN_PIN    = 7;
const int LED_RED_PIN      = 8;
const int BUZZER_PIN       = 13;

float targetPan = 90.0, currentPan = 90.0;
float currentTilt = 90.0;
float integralError = 0.0, previousError = 0.0;

const float BASE_KP = 0.6, BASE_KI = 0.02, BASE_KD = 0.15;
const float THRESHOLD_DEGRADED = 0.5;
const float THRESHOLD_AT_RISK  = 1.2;

// New thresholds for the v7 additions
const float COLD_THRESHOLD_C     = -10.0;  // below this, "heater" indication activates
const float ENGAGEMENT_RANGE_CM  = 30.0;   // closer than this = "engagement zone"
const int   TREND_WINDOW         = 5;      // how many samples the trend check looks back

bool manualOverride = false;
bool lastButtonState = HIGH;
bool blinkState = false;
unsigned long lastBlinkToggle = 0;
const unsigned long blinkIntervalMs = 250;

float errorHistory[5] = {0, 0, 0, 0, 0};
int errorHistoryIndex = 0;

unsigned long lastUpdateTime = 0;
unsigned long lastLcdUpdate = 0;
const unsigned long updateInterval = 100;
const unsigned long lcdInterval = 400;

void setup() {
  Serial.begin(9600);
  panServo.attach(PAN_SERVO_PIN);
  tiltServo.attach(TILT_SERVO_PIN);
  panServo.write((int)currentPan);
  tiltServo.write((int)currentTilt);

  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(MODE_BUTTON_PIN, INPUT_PULLUP);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("C-UAS CONSOLE v7");
  lcd.setCursor(0, 1);
  lcd.print("Thermal+Predict");
  delay(1200);
  lcd.clear();

  Serial.println("Multi-Sensor Gimbal Console v7");
  Serial.println("Adds: thermal indication, engagement-zone trigger, trend detection");
  Serial.println("---------------------------------------------------------------");
}

float readWindSpeed() {
  return (analogRead(WIND_POT_PIN) / 1023.0) * 25.0;
}

float readSimulatedTemp() {
  return -40.0 + (analogRead(TEMP_POT_PIN) / 1023.0) * 60.0;
}

float readRangeCm() {
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 25000);
  if (duration == 0) return -1;
  return duration * 0.0343 / 2.0;
}

void computeScheduledGains(float tempC, float windSpeed, float &kp, float &kd, float &ki) {
  float coldFactor = max(0.0f, (0.0f - tempC)) / 40.0f;
  float windFactor = windSpeed / 25.0f;
  float severity = constrain(coldFactor * 0.5f + windFactor * 0.5f, 0.0f, 1.0f);
  kp = BASE_KP * (1 + 0.35f * severity);
  ki = BASE_KI * (1 - 0.2f * severity);
  kd = BASE_KD * (1 + 0.25f * severity);
}

// Simple linear trend check: is the average of the newer half of the
// history window clearly higher than the older half? If so, error is
// trending worse even though it may not have crossed a hard threshold yet.
bool isErrorTrendingWorse() {
  float oldAvg = (errorHistory[0] + errorHistory[1]) / 2.0;
  float newAvg = (errorHistory[3] + errorHistory[4]) / 2.0;
  return (abs(newAvg) - abs(oldAvg)) > 0.15; // trend sensitivity
}

void updateStatusIndicators(float absError) {
  unsigned long now = millis();
  if (absError < THRESHOLD_DEGRADED) {
    digitalWrite(LED_GREEN_PIN, HIGH);
    digitalWrite(LED_RED_PIN, LOW);
  } else if (absError < THRESHOLD_AT_RISK) {
    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(LED_RED_PIN, HIGH);
  } else {
    digitalWrite(LED_GREEN_PIN, LOW);
    if (now - lastBlinkToggle >= blinkIntervalMs) {
      lastBlinkToggle = now;
      blinkState = !blinkState;
    }
    digitalWrite(LED_RED_PIN, blinkState ? HIGH : LOW);
  }
}

void checkOverrideToggle() {
  bool buttonState = digitalRead(MODE_BUTTON_PIN);
  if (buttonState == LOW && lastButtonState == HIGH) {
    manualOverride = !manualOverride;
    integralError = 0;
  }
  lastButtonState = buttonState;
}

void loop() {
  unsigned long now = millis();
  checkOverrideToggle();
  if (now - lastUpdateTime < updateInterval) return;
  float dt = (now - lastUpdateTime) / 1000.0;
  lastUpdateTime = now;

  float windSpeed = readWindSpeed();
  float tempC = readSimulatedTemp();
  float rangeCm = readRangeCm();
  float error;

  if (manualOverride) {
    targetPan = map(analogRead(MANUAL_PAN_PIN), 0, 1023, 0, 180);
    currentPan = targetPan;
    currentTilt = map(analogRead(MANUAL_TILT_PIN), 0, 1023, 60, 120);
    error = 0;
    integralError = 0;
  } else {
    float disturbance = (windSpeed / 25.0) * 15.0;
    currentPan += (random(-100, 100) / 100.0) * (disturbance / 10.0);

    float kp, ki, kd;
    computeScheduledGains(tempC, windSpeed, kp, kd, ki);

    error = targetPan - currentPan;
    integralError += error * dt;
    integralError = constrain(integralError, -50, 50);
    float derivative = (error - previousError) / dt;
    previousError = error;

    float correction = kp * error + ki * integralError + kd * derivative;
    currentPan += correction * dt;
    currentPan = constrain(currentPan, 0, 180);

    if (rangeCm > 0) {
      currentTilt = constrain(90 + (rangeCm - 50) * 0.3, 60, 120);
    }
  }

  panServo.write((int)currentPan);
  tiltServo.write((int)currentTilt);
  updateStatusIndicators(abs(error));

  // record error history for trend detection
  errorHistory[errorHistoryIndex] = error;
  errorHistoryIndex = (errorHistoryIndex + 1) % TREND_WINDOW;
  bool trendWarning = isErrorTrendingWorse();

  bool heaterOn = (tempC < COLD_THRESHOLD_C);
  bool inEngagementZone = (rangeCm > 0 && rangeCm < ENGAGEMENT_RANGE_CM);
  bool armed = inEngagementZone && (abs(error) < THRESHOLD_DEGRADED) && !manualOverride;

  // Sound priority: AT_RISK alert > armed tone > silence
  if (abs(error) >= THRESHOLD_AT_RISK) {
    tone(BUZZER_PIN, 1000); // critical environmental alert (blinking red, from updateStatusIndicators)
  } else if (armed) {
    tone(BUZZER_PIN, 1500); // steady engagement-zone armed tone, distinct pitch
  } else {
    noTone(BUZZER_PIN);
  }

  if (now - lastLcdUpdate >= lcdInterval) {
    lastLcdUpdate = now;
    lcd.clear();
    lcd.setCursor(0, 0);
    if (heaterOn) {
      lcd.print("HEATER:ON T:");
      lcd.print((int)tempC);
    } else if (trendWarning) {
      lcd.print("TREND WARN");
    } else {
      lcd.print(manualOverride ? "MANUAL " : "AUTO ");
      lcd.print("R:");
      if (rangeCm > 0) lcd.print((int)rangeCm); else lcd.print("--");
    }
    lcd.setCursor(0, 1);
    if (armed) {
      lcd.print("NEUTRALIZE ARMED");
    } else {
      lcd.print("P:"); lcd.print((int)currentPan);
      lcd.print(" T:"); lcd.print((int)currentTilt);
      lcd.print(abs(error) >= THRESHOLD_AT_RISK ? " ALM" : "");
    }
  }

  Serial.print("Mode: "); Serial.print(manualOverride ? "MANUAL" : "AUTO");
  Serial.print(" | Wind: "); Serial.print(windSpeed, 1);
  Serial.print(" m/s | Temp: "); Serial.print(tempC, 1);
  Serial.print(" C | Heater: "); Serial.print(heaterOn ? "ON" : "off");
  Serial.print(" | Range: "); Serial.print(rangeCm >= 0 ? rangeCm : -1);
  Serial.print(" cm | Armed: "); Serial.print(armed ? "YES" : "no");
  Serial.print(" | Trend: "); Serial.print(trendWarning ? "WORSENING" : "stable");
  Serial.print(" | Pan: "); Serial.print(currentPan, 1);
  Serial.print(" Tilt: "); Serial.print(currentTilt, 1);
  Serial.print(" | Error: "); Serial.println(error, 1);
}

