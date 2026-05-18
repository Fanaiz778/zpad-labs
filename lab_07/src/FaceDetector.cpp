#include "FaceDetector.hpp"

#include <algorithm>
#include <chrono>
#include <stdexcept>
#include <thread>

FaceDetector::FaceDetector(const std::string& modelConfig, const std::string& modelWeights)
    : running(true),
      hasNewFrame(false),
      artificialDelayEnabled(false) {
    net = cv::dnn::readNetFromCaffe(modelConfig, modelWeights);

    if (net.empty()) {
        throw std::runtime_error("Cannot load face detection model.");
    }

    workerThread = std::thread(&FaceDetector::workerLoop, this);
}

FaceDetector::~FaceDetector() {
    running = false;
    conditionVariable.notify_all();

    if (workerThread.joinable()) {
        workerThread.join();
    }
}

void FaceDetector::submitFrame(const cv::Mat& frame) {
    if (frame.empty()) {
        return;
    }

    {
        std::lock_guard<std::mutex> lock(mutex);
        latestFrame = frame.clone();
        hasNewFrame = true;
    }

    conditionVariable.notify_one();
}

std::vector<cv::Rect> FaceDetector::getFaces() {
    std::lock_guard<std::mutex> lock(mutex);
    return latestFaces;
}

void FaceDetector::setArtificialDelay(bool enabled) {
    artificialDelayEnabled = enabled;
}

void FaceDetector::workerLoop() {
    while (running) {
        cv::Mat frameForDetection;

        {
            std::unique_lock<std::mutex> lock(mutex);
            conditionVariable.wait(lock, [this]() {
                return hasNewFrame || !running;
            });

            if (!running) {
                break;
            }

            frameForDetection = latestFrame.clone();
            hasNewFrame = false;
        }

        if (frameForDetection.empty()) {
            continue;
        }

        std::vector<cv::Rect> faces = detectFaces(frameForDetection);

        {
            std::lock_guard<std::mutex> lock(mutex);
            latestFaces = faces;
        }
    }
}

std::vector<cv::Rect> FaceDetector::detectFaces(const cv::Mat& frame) {
    if (artificialDelayEnabled) {
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    cv::Mat blob = cv::dnn::blobFromImage(
        frame,
        1.0,
        cv::Size(300, 300),
        cv::Scalar(104.0, 177.0, 123.0),
        false,
        false
    );

    net.setInput(blob);
    cv::Mat detections = net.forward();

    cv::Mat detectionMatrix(
        detections.size[2],
        detections.size[3],
        CV_32F,
        detections.ptr<float>()
    );

    std::vector<cv::Rect> faces;

    for (int i = 0; i < detectionMatrix.rows; ++i) {
        float confidence = detectionMatrix.at<float>(i, 2);

        if (confidence > 0.5F) {
            int x1 = static_cast<int>(detectionMatrix.at<float>(i, 3) * frame.cols);
            int y1 = static_cast<int>(detectionMatrix.at<float>(i, 4) * frame.rows);
            int x2 = static_cast<int>(detectionMatrix.at<float>(i, 5) * frame.cols);
            int y2 = static_cast<int>(detectionMatrix.at<float>(i, 6) * frame.rows);

            x1 = std::max(0, std::min(x1, frame.cols - 1));
            y1 = std::max(0, std::min(y1, frame.rows - 1));
            x2 = std::max(0, std::min(x2, frame.cols - 1));
            y2 = std::max(0, std::min(y2, frame.rows - 1));

            cv::Rect faceRect(cv::Point(x1, y1), cv::Point(x2, y2));

            if (faceRect.width > 0 && faceRect.height > 0) {
                faces.push_back(faceRect);
            }
        }
    }

    return faces;
}
