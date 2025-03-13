
#include <Arduino.h>
#include <M5Core2.h>
#include "DcMotorModule.h"
#include "Image.h"
#include <math.h>
#include "Free_Fonts.h"

int16_t RunSpeed = 0;
DcMotorModule DcMotor;

HardwareSerial VSerial(1);
TFT_eSprite tft = TFT_eSprite(&M5.Lcd);

void MoveToLeft(int16_t speed)
{
  DcMotor.MotorRun(0, -speed);
  DcMotor.MotorRun(1, speed);
  DcMotor.MotorRun(2, -speed);
  DcMotor.MotorRun(3, speed);
}

void MoveToRight(int16_t speed)
{
  DcMotor.MotorRun(0, speed);
  DcMotor.MotorRun(1, -speed);
  DcMotor.MotorRun(2, speed);
  DcMotor.MotorRun(3, -speed);
}

void MoveForword(int16_t speed)
{
  DcMotor.MotorRun(0, speed);
  DcMotor.MotorRun(1, speed);
  DcMotor.MotorRun(2, -speed);
  DcMotor.MotorRun(3, -speed);
}

void Search(int16_t speed)
{
  DcMotor.MotorRun(0, speed);
  DcMotor.MotorRun(1, speed);
  DcMotor.MotorRun(2, speed);
  DcMotor.MotorRun(3, speed);
}

void MotorStop()
{
  DcMotor.MotorRun(0, 0);
  DcMotor.MotorRun(1, 0);
  DcMotor.MotorRun(2, 0);
  DcMotor.MotorRun(3, 0);
}


void DisplayInit(void) {     // Initialize the display.
  int bright[4]={30,60,100,200};
  int b=1;
  M5.Lcd.setSwapBytes(true);
  M5.Lcd.setBrightness(bright[b]);
  M5.Lcd.fillScreen(WHITE);  // Set the screen background color to white.
  M5.Lcd.pushImage(0,0,320,240,MC40image);
}

void header(const char *string, uint16_t color) {
    // M5.Lcd.fillScreen(color);
    M5.Lcd.setTextSize(1);
    M5.Lcd.setTextColor(0x4A2D, 0x2E7A);
    M5.Lcd.fillRect(0, 0, 320, 30, 0x2E7A);
    M5.Lcd.setTextDatum(TC_DATUM);
    M5.Lcd.drawString(string, 160, 3, 4);
}


void Clear_circles()
{
  M5.Lcd.fillRect(0, 30, 320, 210, TFT_BLACK);
}

void Draw_Search()
{
  Clear_circles();
  M5.Lcd.drawCircle(320/2,240/2+15,60,TFT_WHITE);
  M5.Lcd.drawCircle(320/2,240/2+15,80,TFT_WHITE);
  M5.Lcd.drawCircle(320/2,240/2+15,100,TFT_WHITE);
  M5.Lcd.fillRect(106,35, 100, 205, TFT_BLACK);

  M5.Lcd.fillRoundRect(135, 80, 44, 111, 5, TFT_CYAN);

  M5.Lcd.setTextColor(TFT_WHITE, TFT_CYAN);
  M5.Lcd.drawCentreString("MC4.0",320/2,240/2+5,4);

}
void setup()
{
    M5.begin(true,true,true,false,kMBusModeOutput);
    Wire1.begin(21,22);

    M5.Lcd.fillScreen(TFT_BLACK);
    header(" MC4.0 AI app", TFT_BLACK);
    Draw_Search();
    
    Serial.begin(115200);

    VSerial.begin(115200, SERIAL_8N1, 13, 14);

    VSerial.write(0xAF);

    Serial.println("Start");
}

int16_t ux;
unsigned long T;
#define BASE_SPEED  20
bool last_dir = false;
bool RunFlag = false;
bool D_Serach = false;
bool RunMotor = true;

void loop()
{
    M5.update();
    if(M5.BtnA.wasReleased())
    {
        //ESP.restart();
        RunMotor = !RunMotor;
    }
    else if(M5.BtnB.wasReleased())
    {
        
    }
    else if (M5.BtnC.wasReleased()) {
      RunFlag = !RunFlag;
      Serial.print("Run Flag = ");
      Serial.println(RunFlag);
      Clear_circles();
      MotorStop();
    }

    if(M5.Touch.ispressed())
  {
    
      RunFlag = !RunFlag;
      Serial.print("Run Flag = ");
      Serial.println(RunFlag);
      Clear_circles();
      Draw_Search();
      MotorStop();
  }


    if(RunFlag)
    {
      Serial.println("run");
      if(VSerial.available())
      {
          VSerial.write(0xAF);

          uint8_t b_data[4];
          VSerial.readBytes(b_data, 4);

          int8_t ux = b_data[0];
          
          uint32_t area = b_data[1] << 16 | b_data[2] << 8 | b_data[3];
          int8_t uy;
          Serial.printf("%d, %d   ,   \n", ux, area);
          
          if(area == 0 && ux == 0)
          {
            if(RunMotor)Search(120);
            if(D_Serach == false)
            {
              Draw_Search();
              D_Serach = true;
            }
          }

          else if(ux != 0)
          {
            Clear_circles();
            int CirclePosition = map(ux,-63,63,0,320);
            int CircleRadius   = map(area,200,75000,5,105);
            M5.Lcd.fillCircle(CirclePosition,240/2+15,CircleRadius,TFT_GREEN);

            RunSpeed = map(ux,-65,65,-255,+255);
            if(RunSpeed < 0)
            {
              if(RunMotor)MoveToRight(abs(RunSpeed));
            }
            else
            {
              if(RunMotor)MoveToLeft(abs(RunSpeed));
            }
            
            D_Serach = false;
          }

          else if(area < 70000)
          {
            Clear_circles();
            int CirclePosition = map(ux,-63,63,0,320);
            int CircleRadius   = map(area,200,75000,5,105);
            M5.Lcd.fillCircle(CirclePosition,240/2+15,CircleRadius,TFT_GREEN);

            RunSpeed = map(area,200,75000,255,0);
            if(RunMotor)MoveForword(RunSpeed);
            D_Serach = false;
          }
      }
    }
}