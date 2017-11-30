#!/usr/bin/env bash

# First all dependencies
sudo apt-get install build-essential cmake git pkg-config &&
sudo apt-get install libjpeg8-dev libtiff4-dev libjasper-dev libpng12-dev &&
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev &&
sudo apt-get install libgtk2.0-dev &&
sudo apt-get install libatlas-base-dev gfortran

VERSION=3.2.0
cd ~
git clone https://github.com/Itseez/opencv.git
cd opencv
git checkout ${VERSION}

cd ~
git clone https://github.com/Itseez/opencv_contrib.git
cd opencv_contrib
git checkout ${VERSION}

cd ~/opencv
mkdir build
cd build

# LAPACK off.
sudo cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules -D WITH_LAPACK=OFF -D BUILD_EXAMPLES=ON .. &&
make -j8 &&
sudo make install &&
sudo ldconfig

echo "Don't forget to symlink to virtualenv."
echo "$ ln -s /usr/local/lib/python3.4/site-packages/cv2.cpython-34m.so cv2.so"


