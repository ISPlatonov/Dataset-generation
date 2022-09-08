import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Qt.labs.platform
import QtQml


Item {
    id: step3photo_num
    //signal gotoMainView()
    signal gotoGeneration()
    signal gotoBacks()
    TextField {
        id: button1
        validator: IntValidator {
            bottom: 1;
        }
        text: manager.photo_num
        focus: true
        horizontalAlignment: TextInput.AlignHCenter
        verticalAlignment: TextInput.AlignVCenter
        font.pointSize: 24
        width: (parent.width / 2)
        anchors.centerIn: parent
        height: manager.config.graphics.unit_height
        onTextEdited: {
            manager.photo_num = text
            console.log("photo num = " + text)
        }
    }
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step3photo_num.gotoBacks()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: step3photo_num.gotoGeneration()
    }
    FolderDialog {
        id: fileDialog
        //nameFilters: ["*/"]
        //selectFolder: true
    }
    Loader {
        id: backsloader
        anchors.fill: parent
    }
    Keys.onUpPressed: manager.photo_num++
    Keys.onDownPressed: manager.photo_num--
    Keys.onEnterPressed: step3photo_num.gotoGeneration()
    Keys.onEscapePressed: step3photo_num.gotoBacks()
}
