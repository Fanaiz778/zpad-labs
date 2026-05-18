#include <opencv2/opencv.hpp>

#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "CameraProvider.hpp"
#include "Display.hpp"
#include "FaceDetector.hpp"
#include "FrameProcessor.hpp"
#include "KeyProcessor.hpp"

namespace {
FrameProcessor* globalFrameProcessor = nullptr;

bool isDrawing = false;
cv::Point drawStart;
cv::Point drawEnd;

int brightness = 100;

void onMouse(int event, int x, int y, int flags, void*) {
    if (globalFrameProcessor == nullptr) {
        return;
    }

    if (event == cv::EVENT_LBUTTONDOWN) {
        isDrawing = true;
        drawStart = cv::Point(x, y);
        drawEnd = drawStart;
        globalFrameProcessor->setDrawingState(true, drawStart, drawEnd);
    } else if (event == cv::EVENT_MOUSEMOVE && isDrawing) {
        drawEnd = cv::Point(x, y);
        globalFrameProcessor->setDrawingState(true, drawStart, drawEnd);
    } else if (event == cv::EVENT_LBUTTONUP) {
        isDrawing = false;
        drawEnd = cv::Point(x, y);

        int left = std::min(drawStart.x, drawEnd.x);
        int top = std::min(drawStart.y, drawEnd.y);
        int width = std::abs(drawEnd.x - drawStart.x);
        int height = std::abs(drawEnd.y - drawStart.y);

        globalFrameProcessor->addRectangle(cv::Rect(left, top, width, height));
        globalFrameProcessor->setDrawingState(false, drawStart, drawEnd);
    } else if (event == cv::EVENT_MOUSEWHEEL) {
        int wheelDelta = cv::getMouseWheelDelta(flags);
        globalFrameProcessor->changeZoomByMouseWheel(wheelDelta);
    }
}

void drawFaces(cv::Mat& frame, const std::vector<cv::Rect>& faces) {
    for (const auto& face : faces) {
        cv::rectangle(frame, face, cv::Scalar(0, 255, 255), 2);
        cv::putText(
            frame,
            "Face",
            cv::Point(face.x, std::max(face.y - 10, 0)),
            cv::FONT_HERSHEY_SIMPLEX,
            0.7,
            cv::Scalar(0, 255, 255),
            2
        );
    }
}
}

int main() {
    try {
        const std::string windowName = "Lab 07 OpenCV DNN Threads";

        CameraProvider cameraProvider(0);
        KeyProcessor keyProcessor;
        FrameProcessor frameProcessor;
        Display display(windowName);

        FaceDetector faceDetector(
            "models/deploy.prototxt",
            "models/res10_300x300_ssd_iter_140000.caffemodel"
        );

        globalFrameProcessor = &frameProcessor;

        cv::setMouseCallback(windowName, onMouse);
        cv::createTrackbar("Brightness", windowName, &brightness, 200);

        std::cout << "Lab 07 OpenCV DNN Threads started." << std::endl;
        std::cout << "Press F to toggle face detection." << std::endl;
        std::cout << "Press L to toggle artificial detector delay." << std::endl;
        std::cout << "Press ESC to exit." << std::endl;

        while (cameraProvider.isOpened()) {
            cv::Mat frame = cameraProvider.getFrame();

            if (frame.empty()) {
                std::cerr << "Empty frame received." << std::endl;
                break;
            }

            faceDetector.setArtificialDelay(keyProcessor.isDetectorDelayEnabled());

            if (keyProcessor.isFaceDetectionEnabled()) {
                faceDetector.submitFrame(frame);
            }

            cv::Mat processedFrame = frameProcessor.process(
                frame,
                keyProcessor.getMode(),
                brightness,
                keyProcessor.getZoom(),
                keyProcessor.getRotationAngle(),
                keyProcessor.getCrossX(),
                keyProcessor.getCrossY(),
                keyProcessor.isFaceDetectionEnabled(),
                keyProcessor.isDetectorDelayEnabled()
            );

            if (keyProcessor.isFaceDetectionEnabled()) {
                std::vector<cv::Rect> faces = faceDetector.getFaces();
                drawFaces(processedFrame, faces);
            }

            display.show(processedFrame);

            int key = cv::waitKey(1);

            if (key != -1) {
                bool shouldContinue = keyProcessor.processKey(key);

                if (!shouldContinue) {
                    break;
                }
            }
        }

        cv::destroyAllWindows();
    } catch (const std::exception& exception) {
        std::cerr << "Error: " << exception.what() << std::endl;
        return 1;
    }

    return 0;
}
