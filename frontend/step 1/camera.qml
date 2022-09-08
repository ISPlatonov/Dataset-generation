import QtMultimedia
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQml


Item {
    id: step1camera

    signal gotoStep1()
    signal gotoChoosingDir()
    signal gotoStep2()

    property int index: 0  // индекс текущей детали
    property int i: 0  // номер текущей детали
    property bool autoSnapping: true


    function makeSnapshoot() {
        manager.makeDir(manager.name_list[index])
        manager.makeDir(manager.name_list[index]);
        camera.start()
        imageCapture.captureToFile(manager.images_path + "/" + manager.name_list[index] + 
                                   "/" + manager.name_list[index] + "_" + 
                                   "0".repeat(Math.floor(3 - 1 / 10)) + i + ".jpg");
        console.log("i: ", i)
        step1camera.i++;
    }


    Text {
        id: titleText
        anchors.top: parent
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.margins: 50
        text: qsTr("Сделайте фотографии детали " + manager.name_list[index])
    }


    CaptureSession {
        imageCapture : ImageCapture {
            id: imageCapture
            onImageSaved: {
                console.log("image saved")
                if (i == 3) {
                    step1camera.i = 0;
                    step1camera.autoSnapping = false;
                    if (index < manager.name_list.length)
                        index++;
                    else
                        gotoStep2();
                    if (manager.name_list[index].length == 0)
                        if (index < manager.name_list.length - 1)
                            index++;
                        else
                            gotoStep2();
                }
                if (step1camera.autoSnapping == true) {
                    makeSnapshoot()
                }

            }
        }
        camera: Camera {
            id: camera
            cameraDevice: devices.videoInputs[manager.camera_num]
        }

        videoOutput: videoOutput

        Component.onCompleted: {
            camera.start()
        }
    }


    VideoOutput {
        id: videoOutput
        anchors.fill: parent
        focus : visible
    }


    Button {
        id: button1
        text: qsTr("Сделать фотографии")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        onClicked: {
            step1camera.autoSnapping = true;
            makeSnapshoot();
        }
    }


    Button {
        id: buttonMid
        text: qsTr("Одно фото")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        onClicked: {
            step1camera.autoSnapping = false;
            makeSnapshoot();
        }
    }


    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step1camera.gotoStep1()
    }


    MediaDevices {
        id: devices
    }
}
