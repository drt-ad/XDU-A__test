#include <LiquidCrystal.h>

// LCD 引脚定义：RS, E, D4, D5, D6, D7
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// 压力传感器接 A0
const int pressurePin = A0;

// 电机控制引脚
const int motorPin = 7;

// 学号，先暂时用 id 代替
String studentID = "id";

// 压力阈值，默认先设为 100，收到学号后重新计算
float pressureThreshold = 100.0;

// 当前压力值
float pressureValue = 0.0;

// 串口接收缓存
String receivedData = "";

// 标记是否已经收到学号
bool idReceived = false;

void setup() {
  // 初始化 LCD，16列2行
  lcd.begin(16, 2);

  // 电机引脚输出
  pinMode(motorPin, OUTPUT);
  digitalWrite(motorPin, LOW);

  // 串口初始化
  Serial.begin(9600);

  // 开机显示
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("ID:");
  lcd.print(studentID);
  lcd.setCursor(0, 1);
  lcd.print("PRESS:");
  lcd.print(pressureValue, 1);

  delay(1000);
}

void loop() {
  // 读取压力传感器
  int adcValue = analogRead(pressurePin);

// 先算出电压
  float voltage = adcValue * (5.0 / 1023.0);

  // MPX4250 传递函数：Vout = Vcc * (0.00369 * P + 0.04)
  // 反推 P = (Vout / Vcc - 0.04) / 0.00369
  float pressureValue = (voltage / 5.0 - 0.04) / 0.00369-3.5;
  if (idReceived) {
    // 阈值已经在串口接收时计算
  }

  // 电机控制
  if (pressureValue > pressureThreshold) {
    digitalWrite(motorPin, HIGH);  // 电机转动
  } else {
    digitalWrite(motorPin, LOW);   // 电机停止
  }

  // LCD 显示
  lcd.setCursor(0, 0);
  lcd.print("ID:");
  lcd.print(studentID);
  lcd.print("        "); // 清除多余字符

  lcd.setCursor(0, 1);
  lcd.print("PRESS:");
  lcd.print(pressureValue, 1);
  lcd.print("kPa   ");

  // 串口接收处理
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (receivedData.length() > 0) {
        studentID = receivedData;
        idReceived = true;

        // 计算压力阈值：100 + 学号末位数
        char lastChar = studentID.charAt(studentID.length() - 1);
        int lastDigit = lastChar - '0';

        if (lastDigit >= 0 && lastDigit <= 9) {
          pressureThreshold = 100.0 + lastDigit;
        } else {
          pressureThreshold = 100.0;
        }

        // 回传当前压力值
        Serial.print("ID:");
        Serial.print(studentID);
        Serial.print(",PRESS:");
        Serial.print(pressureValue, 1);
        Serial.println("kPa");

        // 清空接收缓存
        receivedData = "";
      }
    } else {
      receivedData += c;
    }
  }

  // 每隔一定时间主动发送一次压力值
  static unsigned long lastSendTime = 0;
  if (millis() - lastSendTime > 500) {
    lastSendTime = millis();

    Serial.print("ID:");
    Serial.print(studentID);
    Serial.print(",PRESS:");
    Serial.print(pressureValue, 1);
    Serial.println("kPa");
  }

  delay(100);
}