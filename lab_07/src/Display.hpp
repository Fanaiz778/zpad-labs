#ifndef DISPLAY_HPP
#define DISPLAY_HPP

#include <opencv2/opencv.hpp>
#include <string>

class Display {
public:
    explicit Display(const std::string& windowName);

    void show(const cv::Mat& frame);
    const std::string& getWindowName() const;

private:
    std::string windowName;
};

#endif
