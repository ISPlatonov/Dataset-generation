import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Qt.labs.platform
import QtQml


Item {
    id: step3dir
    signal gotoMainView()
    signal gotoPhotoNum()
    focus: true
    GridLayout {
        id: layout
        anchors.centerIn: parent
        rows: 5
        columns: 3
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Подтвердите выбор папок для генерации"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Папка с масками деталей"
            }
        }
        TextField {
            id: processed_field
            Layout.columnSpan: 3
            Layout.minimumWidth: 270
            // Layout.maximumWidth: 670
            text: manager.processed_path
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Папка с фонами"
            }
        }
        TextField {
            id: back_field
            Layout.columnSpan: 3
            Layout.minimumWidth: 270
            text: manager.backgrounds_path
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Папка для новых фотографий"
            }
        }
        TextField {
            id: generated_field
            Layout.columnSpan: 3
            Layout.minimumWidth: 270
            text: manager.generated_path
        }
    }
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step3dir.gotoMainView()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: {
            step3dir.gotoPhotoNum();
            manager.processed_path = processed_field.text;
            manager.backgrounds_path = back_field.text;
            manager.generated_path = generated_field.text;
        }
    }
    FolderDialog {
        id: fileDialog
        onAccepted: {
            console.log("dir: " + fileDialog.fileUrls);
        }
        // nameFilters: ["*/"]
        // selectFolder: true
    }
    Loader {
        id: dirloader
        anchors.fill: parent
    }
    Keys.onEscapePressed: {
        step3dir.gotoMainView()
    }
    Keys.onEnterPressed: {
        step3dir.gotoPhotoNum()
    }
}
