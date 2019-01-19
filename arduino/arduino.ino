// fingers: thumb, pointer, middle, ring, little
int fingerPins[5] = {5,8,2,7,3};
bool buttonState[5] = {false, false, false, false, false};
bool newButtonState;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  for (int i=0; i<5; i++) {
    newButtonState = digitalRead(fingerPins[i]);
    if (newButtonState != buttonState[i]) {
      Serial.println(String(i) + " " + String(newButtonState));
      buttonState[i] = newButtonState;
      //debounce
      delay(50);
    }
  }
  delay(1);
}
