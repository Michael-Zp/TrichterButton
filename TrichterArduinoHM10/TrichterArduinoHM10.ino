/*
 *  sketch: SerialPassThrough_SoftwareSerial_NL
 *  www.martyncurrey.com
 *   
 *  Use software serial to talk to serial/UART connected device
 *  What ever is entered in the serial monitor is sent to the connected device
 *  Anything received from the connected device is copied to the serial monitor
 *  User input is echo'd to the serial monitor
 * 
 *  Pins
 *  BT VCC to Arduino 5V out. 
 *  BT GND to GND
 *  Arduino D2 (Arduino RX) 
 *  Arduino D3 (Arduino TX) 
 * 
 *  Assumes a 5V Arduino is being used
 *  If the connected device is 3.3v add a voltage divider (5v to 3.3v) between Arduino TX and device RX
 *  Arduino RX to device TX does not need a voltage divider. The Arduino will see 3.3v as high
 * 
 */

#include <SoftwareSerial.h>
SoftwareSerial softSerial(2, 3); // RX, TX

void print_str_to_bt(const char* msg)
{
    int len = strlen(msg);
    for (int i = 0; i < len; ++i)
    {
        softSerial.write(msg[i]);
    }
}

struct Button {
public:
    Button(
        int pin,
        const char* serialMsgOnPressed,
        const char* btMsgOnPressed,
        const char* serialMsgOnReleased,
        const char* btMsgOnReleased,
        int mode = INPUT) :
        m_pin(pin),
        m_serialMsgOnPressed(serialMsgOnPressed),
        m_btMsgOnPressed(btMsgOnPressed),
        m_serialMsgOnReleased(serialMsgOnReleased),
        m_btMsgOnReleased(btMsgOnReleased),
        m_mode(mode)
    { }

    void setup()
    {
        pinMode(m_pin, m_mode);
    }

    void CheckState()
    {
        int buttonState = digitalRead(m_pin);
        if (buttonState != m_lastButtonState && millis() > m_lastButtonSwitch + s_buttonTimeout)
        {
            if (buttonState == HIGH)
            {
                Serial.write(m_serialMsgOnPressed);
                print_str_to_bt(m_btMsgOnPressed);
            }
            else
            {
                Serial.write(m_serialMsgOnReleased);
                print_str_to_bt(m_btMsgOnReleased);
            }
            m_lastButtonState = buttonState;
        }
    }

private:
    int m_pin;
    const char* m_serialMsgOnPressed;
    const char* m_btMsgOnPressed;
    const char* m_serialMsgOnReleased;
    const char* m_btMsgOnReleased;
    int m_mode;
    int m_lastButtonState = LOW;
    unsigned long m_lastButtonSwitch = 0;

    static const unsigned long s_buttonTimeout = 50;
};

Button trichterBtn(4, "Sending trichter pressed.\n", "tr-pr", "Sending trichter released.\n", "tr-re");
Button volumeUpBtn(5, "Sending volume up pressed.\n", "vu-pr", "Sending volume up released.\n", "vu-re");
Button volumeDownBtn(6, "Sending volume down pressed.\n", "vd-pr", "Sending volume down released.\n", "vd-re");

char c=' ';
boolean NL = true;
 
void setup() 
{
    Serial.begin(9600);
    Serial.print("Sketch:   ");   Serial.println(__FILE__);
    Serial.print("Uploaded: ");   Serial.println(__DATE__);

    softSerial.begin(9600);
    Serial.println("softSerial started at 9600");

    Serial.println("Set line endings to 'Both NL & CR'");

    trichterBtn.setup();
    volumeUpBtn.setup();
    volumeDownBtn.setup();
}
 
void loop()
{
    // Read from the UART module and send to the Serial Monitor
    if (softSerial.available())
    {
        c = softSerial.read();
        Serial.write(c); 
    }
    
    // Read from the Serial Monitor and send to the UART module
    if (Serial.available())
    {
        c = Serial.read();
        
        // do not send line end characters to the HM-10
        if (c!=10 & c!=13 ) { softSerial.write(c); }

        // Echo the user input to the main window. 
        // If there is a new line print the ">" character.
        if (NL) { Serial.print("\r\n>");  NL = false; }
        Serial.write(c);
        if (c==10) { NL = true; }
    }

    trichterBtn.CheckState();
    volumeUpBtn.CheckState();
    volumeDownBtn.CheckState(); 
} // void loop()