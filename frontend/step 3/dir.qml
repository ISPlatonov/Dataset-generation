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
            Layout.columnSpan: 2
            Layout.minimumWidth: 270
            // Layout.maximumWidth: 670
            text: manager.proccessed_path
        }
        Button {
            text: "Изменить"
            height: manager.config.graphics.unit_height
            onClicked: {
                fileDialog.open()
            }
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
            id: text_field2
            Layout.columnSpan: 2
            Layout.minimumWidth: 270
            text: manager.backgrounds_path
        }
        Button {
            text: qsTr("Изменить")
            height: manager.config.graphics.unit_height
            // anchors.verticalCenter: text_field2.verticalCenter
            // Layout.alignment: Qt.AlignVCenter
            onClicked: {
                fileDialog.open()
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Папка для новых сгенерированных фотографий"
            }
        }
        TextField {
            id: text_field3
            Layout.columnSpan: 2
            Layout.minimumWidth: 270
            text: manager.generated_path
        }
        Button {
            Layout.fillHeight: true

            text: qsTr("Изменить")
            height: manager.config.graphics.unit_height
            onClicked: {
                fileDialog.open()
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
        onClicked: step3dir.gotoMainView()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: step3dir.gotoPhotoNum()
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
