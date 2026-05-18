#ifndef FACE_DETECTOR_HPP
#define FACE_DETECTOR_HPP

#include <atomic>
#include <condition_variable>
#include <mutex>
#include <opencv2/dnn.hpp>
#include <opencv2/opencv.hpp>
#include <string>
#include <thread>
#include <vector>

class FaceDetector {
public:
    FaceDetector(const std::string& modelConfig, const std::string& modelWeights);
    ~FaceDetector();

    FaceDetector(const FaceDetector&) = delete;
    FaceDetector& operator=(const FaceDetector&) = delete;

    void submitFrame(const cv::Mat& frame);
    std::vector<cv::Rect> getFaces();
    void setArtificialDelay(bool enabled);

private:
    cv::dnn::Net net;
    std::thread workerThread;
    std::mutex mutex;
    std::condition_variable conditionVariable;

    cv::Mat latestFrame;
    std::vector<cv::Rect> latestFaces;

    std::atomic<bool> running;
    std::atomic<bool> hasNewFrame;
    std::atomic<bool> artificialDelayEnabled;

    void workerLoop();
    std::vector<cv::Rect> detectFaces(const cv::Mat& frame);
};

#endif
