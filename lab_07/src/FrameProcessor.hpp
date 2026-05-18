#ifndef FRAME_PROCESSOR_HPP
#define FRAME_PROCESSOR_HPP

#include <opencv2/opencv.hpp>
#include <string>
#include <vector>

#include "KeyProcessor.hpp"

class FrameProcessor {
public:
    FrameProcessor();

    cv::Mat process(
        const cv::Mat& frame,
        ProcessingMode mode,
        int brightness,
        double zoom,
        double rotationAngle,
        int crossX,
        int crossY,
        bool faceDetectionEnabled,
        bool detectorDelayEnabled
    );

    void setDrawingState(bool isDrawing, cv::Point startPoint, cv::Point endPoint);
    void addRectangle(cv::Rect rectangle);
    void changeZoomByMouseWheel(int wheelDelta);

private:
    bool drawing;
    cv::Point drawStart;
    cv::Point drawEnd;
    std::vector<cv::Rect> rectangles;
    double mouseWheelZoomFactor;

    cv::Mat applyMode(const cv::Mat& frame, ProcessingMode mode);
    cv::Mat applyTransformations(const cv::Mat& frame, double zoom, double rotationAngle);
    cv::Mat applyGlitch(const cv::Mat& frame);
    void drawOverlay(
        cv::Mat& frame,
        ProcessingMode mode,
        int crossX,
        int crossY,
        int brightness,
        bool faceDetectionEnabled,
        bool detectorDelayEnabled
    );
    std::string modeToString(ProcessingMode mode) const;
};

#endif
