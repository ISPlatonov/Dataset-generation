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
    Column {
        anchors.centerIn: parent
        spacing: 2
        Text {
            text: qsTr("Генерация масок")
        }
        Button {
            text: qsTr("Запустить")
            onClicked: {
                manager.handSegmentor()
            }
        }
        // ProgressBar {
        //     value: manager.hsStatus
        // }
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
     Button {
        text: qsTr("На следующий этап")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: step2threshold.gotoStep3()
    }
    Loader {
        id: thresholdloader
        anchors.fill: parent
    }
    // Connections {  // why?
    //     target: manager
 
    //     onHsEnded: {
    //         gotoStep3()
    //     }
    // }
}
