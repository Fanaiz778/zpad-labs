#include "Display.hpp"

Display::Display(const std::string& windowName)
    : windowName(windowName) {
    cv::namedWindow(windowName);
}

void Display::show(const cv::Mat& frame) {
    cv::imshow(windowName, frame);
}

const std::string& Display::getWindowName() const {
    return windowName;
}
