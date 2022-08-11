import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
import QtQml 2.0
/*
1) Загрузить фотку
2) Привязать ползунок к фотке (цветопорог)
*/
Item {
    id: step2threshold
    signal gotoMainView()
    signal gotoStep2()
    signal gotoStep3()
    //signal handSegmentor()
    Image {
        id: photoPreview
        width: parent.width
        height: parent.height
        anchors.margins: 100
        source: "batman_001.jpg"
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
            gotoStep3()
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
}
