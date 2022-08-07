import QtMultimedia 5.0
import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
import QtQml 2.0


Item {
    id: step1camera
    width: 640
    height: 360

    signal gotoStep1()
    signal gotoChoosingDir()
    //signal makeSnapshoot()
    signal gotoStep2()

    property int index: 0  // НОМЕР ТЕКУЩЕЙ ДЕТАЛИ, КОТОРУЮ ФОТКАЕМ
    property bool imC: true
    property bool imS: true
    property bool readyForSnap: true


    function makeSnapshoot() {
        console.log("index: " + index + ", len: " + manager.name_list.length)
        manager.makeDir(manager.name_list[index]);
        for (var i = 0; i < 10; i++) {
            camera.start()
            imC = false;
            imS = false;
            readyForSnap = false;
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

    Camera {
        id: camera

        imageProcessing.whiteBalanceMode: CameraImageProcessing.WhiteBalanceFlash

        exposure {
            exposureCompensation: -1.0
            exposureMode: Camera.ExposurePortrait
        }

        flash.mode: Camera.FlashRedEyeReduction

        imageCapture {
            onImageCaptured: {
                imC = true;
                if (imC & imS)
                    readyForSnap: true
            }
            onImageSaved: {
                imS = true;
                if (imC & imS)
                    readyForSnap: true
            }
        }
    }

    VideoOutput {
        source: camera
        anchors.fill: parent
        focus : visible
    }

    Image {
        id: photoPreview
    }
    Button {
        id: button1
        text: qsTr("Сделать фотографии")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        onClicked: {
            makeSnapshoot()
        } // заглушка
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
