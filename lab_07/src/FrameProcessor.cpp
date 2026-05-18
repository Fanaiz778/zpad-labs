#include "FrameProcessor.hpp"

#include <algorithm>
#include <cmath>
#include <string>
#include <vector>

FrameProcessor::FrameProcessor()
    : drawing(false),
      drawStart(0, 0),
      drawEnd(0, 0),
      mouseWheelZoomFactor(1.0) {}

cv::Mat FrameProcessor::process(
    const cv::Mat& frame,
    ProcessingMode mode,
    int brightness,
    double zoom,
    double rotationAngle,
    int crossX,
    int crossY,
    bool faceDetectionEnabled,
    bool detectorDelayEnabled
) {
    cv::Mat adjusted;
    frame.convertTo(adjusted, -1, 1.0, brightness - 100);

    cv::Mat transformed = applyTransformations(adjusted, zoom * mouseWheelZoomFactor, rotationAngle);
    cv::Mat processed = applyMode(transformed, mode);

    drawOverlay(processed, mode, crossX, crossY, brightness, faceDetectionEnabled, detectorDelayEnabled);

    return processed;
}

cv::Mat FrameProcessor::applyMode(const cv::Mat& frame, ProcessingMode mode) {
    cv::Mat result;

    switch (mode) {
        case ProcessingMode::Normal:
            result = frame.clone();
            break;

        case ProcessingMode::Invert:
            cv::bitwise_not(frame, result);
            break;

        case ProcessingMode::GaussianBlur:
            cv::GaussianBlur(frame, result, cv::Size(15, 15), 0);
            break;

        case ProcessingMode::Canny: {
            cv::Mat gray;
            cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
            cv::Canny(gray, result, 80, 160);
            cv::cvtColor(result, result, cv::COLOR_GRAY2BGR);
            break;
        }

        case ProcessingMode::Sobel: {
            cv::Mat gray;
            cv::Mat gradX;
            cv::Mat gradY;
            cv::Mat absGradX;
            cv::Mat absGradY;

            cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
            cv::Sobel(gray, gradX, CV_16S, 1, 0, 3);
            cv::Sobel(gray, gradY, CV_16S, 0, 1, 3);
            cv::convertScaleAbs(gradX, absGradX);
            cv::convertScaleAbs(gradY, absGradY);
            cv::addWeighted(absGradX, 0.5, absGradY, 0.5, 0, result);
            cv::cvtColor(result, result, cv::COLOR_GRAY2BGR);
            break;
        }

        case ProcessingMode::Grayscale:
            cv::cvtColor(frame, result, cv::COLOR_BGR2GRAY);
            cv::cvtColor(result, result, cv::COLOR_GRAY2BGR);
            break;

        case ProcessingMode::Binary: {
            cv::Mat gray;
            cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);
            cv::threshold(gray, result, 127, 255, cv::THRESH_BINARY);
            cv::cvtColor(result, result, cv::COLOR_GRAY2BGR);
            break;
        }

        case ProcessingMode::Glitch:
            result = applyGlitch(frame);
            break;
    }

    return result;
}

cv::Mat FrameProcessor::applyTransformations(const cv::Mat& frame, double zoom, double rotationAngle) {
    cv::Mat result;
    cv::Point2f center(frame.cols / 2.0F, frame.rows / 2.0F);

    cv::Mat rotationMatrix = cv::getRotationMatrix2D(center, rotationAngle, zoom);
    cv::warpAffine(frame, result, rotationMatrix, frame.size());

    return result;
}

cv::Mat FrameProcessor::applyGlitch(const cv::Mat& frame) {
    std::vector<cv::Mat> channels;
    cv::split(frame, channels);

    cv::Mat shiftedBlue;
    cv::Mat shiftedGreen;
    cv::Mat shiftedRed;

    cv::Mat matrixBlue = (cv::Mat_<double>(2, 3) << 1, 0, -10, 0, 1, 0);
    cv::Mat matrixGreen = (cv::Mat_<double>(2, 3) << 1, 0, 0, 0, 1, 0);
    cv::Mat matrixRed = (cv::Mat_<double>(2, 3) << 1, 0, 10, 0, 1, 0);

    cv::warpAffine(channels[0], shiftedBlue, matrixBlue, frame.size());
    cv::warpAffine(channels[1], shiftedGreen, matrixGreen, frame.size());
    cv::warpAffine(channels[2], shiftedRed, matrixRed, frame.size());

    std::vector<cv::Mat> shiftedChannels = {shiftedBlue, shiftedGreen, shiftedRed};

    cv::Mat result;
    cv::merge(shiftedChannels, result);

    return result;
}

void FrameProcessor::drawOverlay(
    cv::Mat& frame,
    ProcessingMode mode,
    int crossX,
    int crossY,
    int brightness,
    bool faceDetectionEnabled,
    bool detectorDelayEnabled
) {
    cv::Scalar green(0, 255, 0);
    cv::Scalar red(0, 0, 255);
    cv::Scalar white(255, 255, 255);

    cv::line(frame, cv::Point(crossX - 20, crossY), cv::Point(crossX + 20, crossY), green, 2);
    cv::line(frame, cv::Point(crossX, crossY - 20), cv::Point(crossX, crossY + 20), green, 2);

    for (const auto& rectangle : rectangles) {
        cv::rectangle(frame, rectangle, red, 2);
    }

    if (drawing) {
        cv::rectangle(frame, drawStart, drawEnd, white, 2);
    }

    cv::putText(frame, "Mode: " + modeToString(mode), cv::Point(20, 30),
                cv::FONT_HERSHEY_SIMPLEX, 0.8, white, 2);

    cv::putText(frame, "Brightness: " + std::to_string(brightness), cv::Point(20, 60),
                cv::FONT_HERSHEY_SIMPLEX, 0.8, white, 2);

    std::string faceStatus = faceDetectionEnabled ? "Face detection: ON" : "Face detection: OFF";
    cv::putText(frame, faceStatus, cv::Point(20, 90),
                cv::FONT_HERSHEY_SIMPLEX, 0.8, white, 2);

    std::string delayStatus = detectorDelayEnabled ? "Detector delay: ON" : "Detector delay: OFF";
    cv::putText(frame, delayStatus, cv::Point(20, 120),
                cv::FONT_HERSHEY_SIMPLEX, 0.8, white, 2);

    cv::putText(frame,
                "1-8 modes | F face | L delay | WASD cross | Q/E rotate | +/- zoom | R reset | ESC exit",
                cv::Point(20, frame.rows - 20),
                cv::FONT_HERSHEY_SIMPLEX, 0.55,
                white,
                2);
}

std::string FrameProcessor::modeToString(ProcessingMode mode) const {
    switch (mode) {
        case ProcessingMode::Normal:
            return "Normal";
        case ProcessingMode::Invert:
            return "Invert";
        case ProcessingMode::GaussianBlur:
            return "Gaussian Blur";
        case ProcessingMode::Canny:
            return "Canny";
        case ProcessingMode::Sobel:
            return "Sobel";
        case ProcessingMode::Grayscale:
            return "Grayscale";
        case ProcessingMode::Binary:
            return "Binary";
        case ProcessingMode::Glitch:
            return "Glitch";
    }

    return "Unknown";
}

void FrameProcessor::setDrawingState(bool isDrawing, cv::Point startPoint, cv::Point endPoint) {
    drawing = isDrawing;
    drawStart = startPoint;
    drawEnd = endPoint;
}

void FrameProcessor::addRectangle(cv::Rect rectangle) {
    if (rectangle.width > 0 && rectangle.height > 0) {
        rectangles.push_back(rectangle);
    }
}

void FrameProcessor::changeZoomByMouseWheel(int wheelDelta) {
    if (wheelDelta > 0) {
        mouseWheelZoomFactor += 0.1;
    } else {
        mouseWheelZoomFactor -= 0.1;
    }

    mouseWheelZoomFactor = std::clamp(mouseWheelZoomFactor, 0.5, 3.0);
}
