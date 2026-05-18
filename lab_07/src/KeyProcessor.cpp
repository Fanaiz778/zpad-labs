#include "KeyProcessor.hpp"

KeyProcessor::KeyProcessor()
    : mode(ProcessingMode::Normal),
      zoom(1.0),
      rotationAngle(0.0),
      crossX(100),
      crossY(100),
      faceDetectionEnabled(false),
      detectorDelayEnabled(false) {}

bool KeyProcessor::processKey(int key) {
    if (key == 27) {
        return false;
    }

    switch (key) {
        case '1':
            mode = ProcessingMode::Normal;
            break;
        case '2':
            mode = ProcessingMode::Invert;
            break;
        case '3':
            mode = ProcessingMode::GaussianBlur;
            break;
        case '4':
            mode = ProcessingMode::Canny;
            break;
        case '5':
            mode = ProcessingMode::Sobel;
            break;
        case '6':
            mode = ProcessingMode::Grayscale;
            break;
        case '7':
            mode = ProcessingMode::Binary;
            break;
        case '8':
            mode = ProcessingMode::Glitch;
            break;
        case 'f':
        case 'F':
            faceDetectionEnabled = !faceDetectionEnabled;
            break;
        case 'l':
        case 'L':
            detectorDelayEnabled = !detectorDelayEnabled;
            break;
        case 'w':
        case 'W':
            crossY -= 10;
            break;
        case 's':
        case 'S':
            crossY += 10;
            break;
        case 'a':
        case 'A':
            crossX -= 10;
            break;
        case 'd':
        case 'D':
            crossX += 10;
            break;
        case 'q':
        case 'Q':
            rotationAngle -= 5.0;
            break;
        case 'e':
        case 'E':
            rotationAngle += 5.0;
            break;
        case '+':
        case '=':
            increaseZoom();
            break;
        case '-':
        case '_':
            decreaseZoom();
            break;
        case 'r':
        case 'R':
            resetTransforms();
            break;
        default:
            break;
    }

    return true;
}

ProcessingMode KeyProcessor::getMode() const {
    return mode;
}

double KeyProcessor::getZoom() const {
    return zoom;
}

double KeyProcessor::getRotationAngle() const {
    return rotationAngle;
}

int KeyProcessor::getCrossX() const {
    return crossX;
}

int KeyProcessor::getCrossY() const {
    return crossY;
}

bool KeyProcessor::isFaceDetectionEnabled() const {
    return faceDetectionEnabled;
}

bool KeyProcessor::isDetectorDelayEnabled() const {
    return detectorDelayEnabled;
}

void KeyProcessor::increaseZoom() {
    zoom += 0.1;
    if (zoom > 3.0) {
        zoom = 3.0;
    }
}

void KeyProcessor::decreaseZoom() {
    zoom -= 0.1;
    if (zoom < 0.5) {
        zoom = 0.5;
    }
}

void KeyProcessor::resetTransforms() {
    zoom = 1.0;
    rotationAngle = 0.0;
    crossX = 100;
    crossY = 100;
}
