#ifndef CAMERA_PROVIDER_HPP
#define CAMERA_PROVIDER_HPP

#include <opencv2/opencv.hpp>

class CameraProvider {
public:
    explicit CameraProvider(int cameraIndex = 0);

    bool isOpened() const;
    cv::Mat getFrame();

private:
    cv::VideoCapture camera;
};

#endif
