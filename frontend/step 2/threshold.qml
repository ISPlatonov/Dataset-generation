import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Qt.labs.platform
import QtQml

Item {
    id: step2threshold
    signal gotoMainView()
    signal gotoStep2()
    signal gotoStep3()
    signal hsEnded()
    Column {
        anchors.centerIn: parent
        spacing: 2
        Text {
            text: qsTr("Генерация масок")
        }
        Button {
            id: button1
            text: qsTr("Запустить")
            onClicked: {
            manager.handSegmentor()
            button1.enabled = false
            button2.enabled = false
            button3.enabled = false
            }
        }
        ProgressBar {
            value: manager.hsStatus
        }
    }
    
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 3)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step2threshold.gotoStep2()
    }
     Button {
        id: button3
        text: qsTr("На следующий этап")
        width: (parent.width / 3)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: step2threshold.gotoStep3()
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
