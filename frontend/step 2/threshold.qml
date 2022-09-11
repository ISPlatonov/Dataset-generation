import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Qt.labs.platform
import QtQml
/*
1) Загрузить фотку
2) Привязать ползунок к фотке (цветопорог)
*/
Item {
    id: step2threshold
    signal gotoMainView()
    signal gotoStep2()
    signal gotoStep3()
    signal hsEnded()
    //signal handSegmentor()
    /*Image {
        id: photoPreview
        width: parent.width
        height: parent.height
        anchors.margins: 100
        source: "images/biba/biba_000.jpg" // manager.images_path + "/" + manager.name_list[0] + "/" + manager.name_list[0] + "_000.jpg"
    }*/
    Column {
        anchors.centerIn: parent
        spacing: 2
        Text {
            text: qsTr("Фильтрация деталей...")
        }
        ProgressBar {
            value: manager.hsStatus
        }
    }
    Button {
        id: button1
        text: qsTr("Подтвердить")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: {
            manager.handSegmentor()
            //console.log("path to image: " + manager.images_path + "/" + manager.name_list[0] + "/" + manager.name_list[0] + "_000.jpg")
            //gotoStep3()
            button1.enabled = false
            button2.enabled = false
            slider.enabled = false
        }
    }
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step2threshold.gotoStep2()
    }
    Slider {
        id: slider
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: button2.verticalCenter
    }
    Loader {
        id: thresholdloader
        anchors.fill: parent
    }
    Connections {
        target: manager
 
        onHsEnded: {
            gotoStep3()
        }
    }
}
