/*
 * helper.h is in the libraries folder, found by Arduino from wherever demo
 * is, a sketch's src folder included.
 */

#include "demo.h"
#include "helper.h"

int demo_answer(void)
{
    return helper_forty() + DEMO_PLUS;
}
