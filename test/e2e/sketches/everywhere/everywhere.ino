// demo from the libraries folder, found by its name.
#include "demo.h"

static_assert(DEMO_PLUS == 2, "the libraries folder's demo should have its default");

void setup()
{
    Serial.begin(115200);
    Serial.println(demo_answer());
}

void loop()
{
}
