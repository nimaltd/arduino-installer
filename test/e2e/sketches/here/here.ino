// demo from this sketch's src folder, found by its path. CI sets DEMO_PLUS to
// 12 in this sketch's copy and installs again, so 12 shows the update kept it.
#include "src/demo/src/demo.h"

static_assert(DEMO_PLUS == 12, "this sketch's own setting should have survived the update");

void setup()
{
    Serial.begin(115200);
    Serial.println(demo_answer());
}

void loop()
{
}
