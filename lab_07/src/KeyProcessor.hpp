#ifndef KEY_PROCESSOR_HPP
#define KEY_PROCESSOR_HPP

enum class ProcessingMode {
    Normal,
    Invert,
    GaussianBlur,
    Canny,
    Sobel,
    Grayscale,
    Binary,
    Glitch
};

class KeyProcessor {
public:
    KeyProcessor();

    bool processKey(int key);

    ProcessingMode getMode() const;
    double getZoom() const;
    double getRotationAngle() const;
    int getCrossX() const;
    int getCrossY() const;
    bool isFaceDetectionEnabled() const;
    bool isDetectorDelayEnabled() const;

    void increaseZoom();
    void decreaseZoom();
    void resetTransforms();

private:
    ProcessingMode mode;
    double zoom;
    double rotationAngle;
    int crossX;
    int crossY;
    bool faceDetectionEnabled;
    bool detectorDelayEnabled;
};

#endif
