import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
import QtQuick.Dialogs 1.2
import QtQml 2.0


Item {
    id: step1dir
    signal gotoStep1()
    signal gotoCamera()
    Button {
        id: button1
        text: qsTr("Выбрать папку с масками деталей")
        width: (parent.width / 2)
        anchors.centerIn: parent
        height: 50
        onClicked: {
            fileDialog.open()
        }
    }
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step1dir.gotoStep1()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: step1dir.gotoCamera()
    }
    FileDialog {
        id: fileDialog
        nameFilters: ["*/"]
        selectFolder: true
    }
    Loader {
        id: dirloader
        anchors.fill: parent
    }
}