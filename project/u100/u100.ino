#define TRIG 9
#define ECHO 8

void setup() {
  Serial.begin(9600);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
}

// ---------- ฟังก์ชันอ่านระยะ (กรองค่าเฉลี่ย 5 ครั้ง) ----------
float readDistanceCM() {
  long sum = 0;
  int validCount = 0;

  for (int i = 0; i < 5; i++) {
    // ส่งคลื่น
    digitalWrite(TRIG, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG, LOW);

    // วัดเวลา echo กลับมา
    long duration = pulseIn(ECHO, HIGH, 30000);  // 30 ms timeout

    // แปลงเป็นเซนติเมตร
    float distance_cm = (duration * 0.0343) / 2.0;

    // กรองค่าผิดปกติ
    if (distance_cm > 0 && distance_cm < 400) {
      sum += distance_cm;
      validCount++;
    }

    delay(20);  // หน่วงนิดหน่อยระหว่างวัด
  }

  if (validCount > 0)
    return sum / validCount;  // คืนค่าระยะเฉลี่ย
  else
    return -1;  // ถ้าไม่มีค่า valid
}

void loop() {
  float distance = readDistanceCM();

  if (distance > 0) {
    Serial.print(distance);
    Serial.println(" cm");
  } else {
    Serial.println("Out of range or invalid");
  }

  delay(200);
}
