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
    property int detailNumber: 0  // НОМЕР ТЕКУЩЕЙ ДЕТАЛИ, КОТОРУЮ ФОТКАЕМ
    Text {
        id: titleText
        anchors.top: parent
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.margins: 50
        text: qsTr("\nСделайте фотографии детали "+firstStepArray[0])
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
                photoPreview.source = preview  // Show the preview in an Image
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
        onClicked: step1camera.gotoMainView()   // заглушка
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
    Loader {
        id: cameraloader
        anchors.fill: parent
    }
}
