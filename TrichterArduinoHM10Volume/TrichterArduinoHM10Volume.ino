#define DEBUG 0
#define VERBOSE 0

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

        if (millis() < m_lastSendTime + s_buttonTimeout)
        {
            return;
        }

        if (buttonState != m_lastButtonState)
        {
            if (buttonState == HIGH)
            {
#if DEBUG
                Serial.write(m_serialMsgOnPressed);
#endif
                print_str_to_bt(m_btMsgOnPressed);
            }
            else
            {
#if DEBUG
                Serial.write(m_serialMsgOnReleased);
#endif
                print_str_to_bt(m_btMsgOnReleased);
            }
            m_lastButtonState = buttonState;
            m_lastSendTime = millis();
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
    unsigned long m_lastSendTime = 0;

    static const unsigned long s_buttonTimeout = 50;
};


struct Dial5V {
public:
    Dial5V(
        uint8_t pin,
        const char* name,
        const char* btPrefix) :
        m_pin(pin),
        m_name(name),
        m_btPrefix(btPrefix)
    { }

    void CheckState()
    {
        int adc_value = analogRead(A0);
        int percentage = constrain((int)(round((float)adc_value / s_adcResolution * 100)), 0, 100);

        if (percentage < s_edgeCutoff)
        {
            percentage = 0;
        }

        if (percentage > 100 - s_edgeCutoff)
        {
            percentage = 100;
        }

        if (percentage < (m_lastSendPercentage - s_percentageDeadzone) || percentage > (m_lastSendPercentage + s_percentageDeadzone))
        {
#if DEBUG
#if VERBOSE
            Serial.write(m_name);
            Serial.write(": Value = ");
            Serial.print(adc_value);
            Serial.write("; New percentage = ");
#endif // VERBOSE
            Serial.println(percentage);
#endif // DEBUG
            print_str_to_bt(m_btPrefix);
            softSerial.write(percentage + 1); // +1 to not send a 0 as this might be bad for string parsing etc

            m_lastSendPercentage = percentage;
            m_lastSendTime = millis();
        }
    }

private:
    uint8_t m_pin;
    const char* m_name;
    const char* m_btPrefix;
    unsigned long m_lastSendTime = 0;
    float m_lastSendPercentage = -1;

    static const float s_percentageDeadzone = 2;
    static const int s_edgeCutoff = 4;
    static const float s_adcResolution = 1024.0;
};

Button trichterBtn(4, "Sending trichter pressed.\n", "tr-pr", "Sending trichter released.\n", "tr-re");
Dial5V volumeDial(A0, "VolumeDial", "vol-percentage");

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
}
 
void loop()
{
#if DEBUG
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
#endif

    // Analog dial needs to be much more responsive than button
    for (int i = 0; i < 5; ++i)
    {
        volumeDial.CheckState();
        delay(5);
    }

    trichterBtn.CheckState();
    delay(5);
}