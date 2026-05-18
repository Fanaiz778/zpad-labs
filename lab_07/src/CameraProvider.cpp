#include "CameraProvider.hpp"

#include <stdexcept>

CameraProvider::CameraProvider(int cameraIndex) {
    camera.open(cameraIndex);

    if (!camera.isOpened()) {
        throw std::runtime_error("Cannot open camera.");
    }

    camera.set(cv::CAP_PROP_FRAME_WIDTH, 1280);
    camera.set(cv::CAP_PROP_FRAME_HEIGHT, 720);
}

bool CameraProvider::isOpened() const {
    return camera.isOpened();
}

cv::Mat CameraProvider::getFrame() {
    cv::Mat frame;
    camera >> frame;
    return frame;
}
