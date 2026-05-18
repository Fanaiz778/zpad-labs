# Лабораторна робота №6

## Тема

C++ OpenCV

## Мета роботи

Створити C++ програму з використанням OpenCV, яка читає відео з камери, відображає його у вікні, реагує на клавіатуру та мишу і перемикає різні режими обробки зображень.

## Структура директорії

```text
lab_06/
├── README.md
├── CMakeLists.txt
├── preinstall.sh
├── build.sh
├── run.sh
└── src/
    ├── main.cpp
    ├── CameraProvider.hpp
    ├── CameraProvider.cpp
    ├── KeyProcessor.hpp
    ├── KeyProcessor.cpp
    ├── FrameProcessor.hpp
    ├── FrameProcessor.cpp
    ├── Display.hpp
    └── Display.cpp
```

## Вимоги до системи

- Linux / Ubuntu 22.04 або новіше
- GCC / G++ 11 або новіше
- CMake 3.16 або новіше
- OpenCV
- Make
- Камера або webcam

## Встановлення залежностей

```bash
chmod +x preinstall.sh
./preinstall.sh
```

## Збірка проєкту

```bash
chmod +x build.sh
./build.sh
```

## Запуск програми

```bash
chmod +x run.sh
./run.sh
```

## Керування програмою

Після запуску відкриється вікно з відео з камери.

Клавіші:

| Клавіша | Дія |
|---|---|
| `1` | Звичайне зображення |
| `2` | Інверсія кольорів |
| `3` | Gaussian Blur |
| `4` | Canny filter |
| `5` | Sobel filter |
| `6` | Grayscale |
| `7` | Binary threshold |
| `8` | Glitch effect |
| `W`, `A`, `S`, `D` | Переміщення хрестика |
| `Q`, `E` | Обертання зображення |
| `+`, `-` | Зум |
| `R` | Скидання трансформацій |
| `ESC` | Вихід |

Миша:

- ЛКМ натиснути та потягнути — намалювати прямокутник.
- Колесо миші вгору/вниз — зум.

Слайдер:

- `Brightness` змінює яскравість кадру.

## Архітектура

- `CameraProvider` — читає кадри з камери через `cv::VideoCapture`.
- `KeyProcessor` — обробляє натиснуті клавіші та перемикає режими.
- `FrameProcessor` — виконує обробку кадрів залежно від активного режиму.
- `Display` — відповідає за показ кадру через `cv::imshow`.
- `main.cpp` — створює об'єкти класів і містить основний цикл програми.

## Примітка

Проєкт збирається через CMake + Make. Після `git clone` очікуваний запуск:

```bash
./preinstall.sh
./build.sh
./run.sh
```
