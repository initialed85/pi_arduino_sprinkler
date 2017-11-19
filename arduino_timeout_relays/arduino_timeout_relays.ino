const int numRelays = 4;
const int relayTimeout = 5;

int relayPins[numRelays] = {2, 3, 4, 5};
int relayNumbers[numRelays] = {1, 2, 3, 4};
int relayStates[numRelays] = {0, 0, 0, 0};
int relayCounters[numRelays] = {0, 0, 0, 0};

int loopCounter = 100;

void setup() {
  for (int i = 0; i < numRelays; i++ ) {
    int pin = relayPins[i];
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }

  Serial.begin(9600);
  Serial.setTimeout(10);
  Serial.println("DEBUG: setup() complete");
}

int getRelayPinFromIndex(int index) {
  return relayPins[index];
}

int getRelayNumberFromIndex(int index) {
  return relayNumbers[index];
}

int getRelayIndexFromNumber(int number) {
  for (int i = 0; i < numRelays; i++) {
    if (relayNumbers[i] == number) {
      return i;
    }
  }

  return -1;
}

bool setRelayState(int index, int state) {
  int *relayState = &relayStates[index];
  int *relayCounter = &relayCounters[index];
  int relayPin = relayPins[index];

  if (state == 1) {
    *relayCounter = relayTimeout;
    if (*relayState != state) {
      digitalWrite(relayPin, HIGH);
      *relayState = 1;
    }
  } else if (*relayState != state) {
    *relayCounter = 0;
    digitalWrite(relayPin, LOW);
    *relayState = 0;
  }

  return false;
}

void handleRelayCounters() {
  for (int i = 0; i < numRelays; i++) {
    int *relayCounter = &relayCounters[i];

    if (*relayCounter > 0) {
      *relayCounter = *relayCounter - 1;
    }
  }
}

bool handleLoopCounter() {
  if (loopCounter == 0) {
    loopCounter = 100;
    return true;
  }

  loopCounter--;

  return false;
}

void handleSerialRead() {
  if (!Serial.available()) {
    return;
  }

  int relayNumber = Serial.parseInt();

  if (relayNumber == 0) {
    Serial.println("ERROR: expected int, got something else");
    return;
  }

  int relayIndex = getRelayIndexFromNumber(relayNumber);
  if (relayIndex == -1) {
    Serial.print("ERROR: relay ");
    Serial.print(relayNumber);
    Serial.println(" unknown");
    return;
  }

  char readBuffer[16];

  Serial.readBytesUntil(',', readBuffer, 16);
  int bytesRead = Serial.readBytesUntil('\n', readBuffer, 16);
  readBuffer[bytesRead] = '\x0';
  String readData = String(readBuffer);
  readData.trim();
  readData.toLowerCase();

  int relayState = -1;
  String relayFriendlyState;

  if (readData.startsWith("on")) {
    relayState = 1;
    relayFriendlyState = "on";
  } else if (readData.startsWith("off")) {
    relayState = 0;
    relayFriendlyState = "off";
  }

  if (relayState == -1) {
    Serial.print("ERROR: state \"");
    Serial.print(readData);
    Serial.println("\" unknown- expected \"on\" of \"off\"");
    return;
  }

  Serial.print("INFO: requesting relay ");
  Serial.print(relayNumber);
  Serial.print(" change to state ");
  Serial.print(relayFriendlyState);
  Serial.println("");
  setRelayState(relayIndex, relayState);
}

void loop() {
  if (handleLoopCounter()) {
    handleRelayCounters();
  }

  handleSerialRead();

  delay(10);
}
