cmake_minimum_required(VERSION 3.16)

project(lab_07_opencv_dnn_threads)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(OpenCV REQUIRED)

include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(src)

add_executable(lab_07
    src/main.cpp
    src/CameraProvider.cpp
    src/KeyProcessor.cpp
    src/FrameProcessor.cpp
    src/FaceDetector.cpp
    src/Display.cpp
)

target_link_libraries(lab_07 ${OpenCV_LIBS} pthread)
