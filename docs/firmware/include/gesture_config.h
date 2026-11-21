#pragma once
#include <Arduino.h>

// Frame contract shared with webcam_sender.py
static constexpr size_t GESTURE_WIDTH = 64;
static constexpr size_t GESTURE_HEIGHT = 64;
static constexpr size_t GESTURE_FRAME_BYTES = GESTURE_WIDTH * GESTURE_HEIGHT;
static constexpr float GESTURE_CONFIDENCE_THRESHOLD = 0.70f;

// Keep class order identical to training/labels.json.
enum GestureClass : uint8_t {
    GESTURE_FIST = 0,
    GESTURE_NO_HAND = 1,
    GESTURE_OPEN_PALM = 2,
    GESTURE_THUMBS_UP = 3,
    GESTURE_VICTORY = 4,
    GESTURE_UNKNOWN = 255
};
