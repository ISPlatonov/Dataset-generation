import QtMultimedia
import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import QtQml


Item {
    MediaDevices {
        id: devices
    }
    id: step1camera

    signal gotoStep1()
    signal gotoChoosingDir()
    //signal makeSnapshoot()
    signal gotoStep2()

    property int index: 0  // НОМЕР ТЕКУЩЕЙ ДЕТАЛИ, КОТОРУЮ ФОТКАЕМ
    property int i: 0  // просто кошмар
    property bool imC: true
    property bool imS: true
    property bool readyForSnap: true


    function snap(i) {
        camera.start()
        console.log("ready: " + camera.ready)
        camera.imageCapture.captureToLocation(manager.images_path + "/" + manager.name_list[index] + "/" + i + ".jpg");
        var imageFile = camera.imageCapture.capturedImagePath;
        console.log("test: " + imageFile);
        //manager.sleepFor(5.);
    }


    function makeSnapshoot() {
        console.log("index: " + index + ", len: " + manager.name_list.length)
        manager.makeDir(manager.name_list[index]);
        for (var i = 0; i < 3; i++) {
            camera.start()
            console.log("ready: " + camera.ready)
            camera.imageCapture.captureToLocation(manager.images_path + "/" + manager.name_list[index] + "/" + i + ".jpg");
            var imageFile = camera.imageCapture.capturedImagePath;
            console.log("test: " + imageFile);
        }
        if (index < manager.name_list.length)
            index++;
        else
            gotoStep2();
        if (manager.name_list[index].length == 0)
            if (index < manager.name_list.length - 1)
                index++;
            else
                gotoStep2();
        console.log("index: " + index + ", len: " + manager.name_list.length)
    }

    Text {
        id: titleText
        anchors.top: parent
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.margins: 50
        text: qsTr("\nСделайте фотографии детали " + manager.name_list[index])
    }
    // НАДО ЗАЦИКЛИТЬ ПОЯВЛЕНИЕ СТРАНИЦЫ ДО ТЕХ ПОР, ПОКА ФОТКИ КАЖДОЙ ДЕТАЛИ НЕ БУДУТ СДЕЛАНЫ

    /*Camera {
        id: camera

        imageProcessing.whiteBalanceMode: CameraImageProcessing.WhiteBalanceFlash

        exposure {
            exposureCompensation: -1.0
            exposureMode: Camera.ExposurePortrait
        }

        flash.mode: Camera.FlashRedEyeReduction
        captureMode: Camera.CaptureStillImage

        imageCapture {
            onImageCaptured: {
                ready: true
                console.log(ready)
            }
        }
    }*/

    CaptureSession {
        imageCapture : ImageCapture {
            id: imageCapture
        }
        camera: Camera {
            id: camera
            cameraDevice: devices.videoInputs[manager.camera_num]
        }

        videoOutput: videoOutput

        Component.onCompleted: {
            //camera.cameraFormat = classPhoto.getCameraFormat();
            camera.start()
        }
    }

    VideoOutput {
        id: videoOutput
        //source: camera
        anchors.fill: parent
        focus : visible
    }

    /*Image {
        id: photoPreview
        source: imageCapture.preview
    }*/

    Button {
        id: button1
        text: qsTr("Сделать фотографии")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        onClicked: {
            //manager.makeDir(manager.name_list[index])
            //snap(step1camera.i)
            console.log("index: " + index + ", len: " + manager.name_list.length)
            manager.makeDir(manager.name_list[index]);
            for (var i = 0; i < 3; i++) {
                camera.start()
                console.log("ready: " + imageCapture.readyForCapture )
                imageCapture.captureToFile(manager.images_path + "/" + manager.name_list[index] + "/" + i + ".jpg");
                //var imageFile = camera.imageCapture.capturedImagePath;
                //console.log("test: " + imageFile);
                //manager.sleepFor(5)
            }
            if (index < manager.name_list.length)
                index++;
            else
                gotoStep2();
            if (manager.name_list[index].length == 0)
                if (index < manager.name_list.length - 1)
                    index++;
                else
                    gotoStep2();
            console.log("index: " + index + ", len: " + manager.name_list.length)
            console.log(camera.cameraStatus)
        } // заглушка
    }
    Button {
        id: buttonMid
        text: qsTr("Одно фото")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        onClicked: {
            manager.makeDir(manager.name_list[index])   // ?
            //snap(step1camera.i)
            console.log("index: " + index + ", len: " + manager.name_list.length)
            manager.makeDir(manager.name_list[index]);

            camera.start()
            console.log("ready: " + camera.ready + ", qqq: " + "0".repeat(Math.floor(3 - 1 / 10)))
            imageCapture.captureToFile(manager.images_path + "/" + manager.name_list[index] + "/" + manager.name_list[index] + "_" + "0".repeat(Math.floor(3 - 1 / 10)) + i + ".jpg");
            //var imageFile = camera.imageCapture.capturedImagePath;
            //console.log("test: " + imageFile);
            step1camera.i++;

            // check i range
            if (i == 3) {
                step1camera.i = 0;
                if (index < manager.name_list.length)
                    index++;
                else
                    gotoStep2();
                if (manager.name_list[index].length == 0)
                    if (index < manager.name_list.length - 1)
                        index++;
                    else
                        gotoStep2();
                console.log("index: " + index + ", len: " + manager.name_list.length)
                console.log(camera.cameraStatus)
            }
            
            
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
}
