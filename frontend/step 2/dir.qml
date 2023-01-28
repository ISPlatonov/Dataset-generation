import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Qt.labs.platform
import QtQml

Item {
    id: step2dir
    signal gotoMainView()
    signal gotoThreshold()
    GridLayout {
        id: layout
        anchors.centerIn: parent
        rows: 8
        columns: 3
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Подтвердите выбор папок для получения масок"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Папка с исходными фотографиями"
            }
        }
        TextField {
            id: raw_photos_text_field
            Layout.columnSpan: 3
            Layout.minimumWidth: 270
            text: manager.raw_photos_path
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Папка для обработанных фотографий"
            }
        }
        TextField {
            id: processed_text_field
            Layout.columnSpan: 3
            Layout.minimumWidth: 270
            text: manager.processed_path
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 2
            Text {
                anchors.centerIn: parent
                text: "Получить roi"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            CheckBox {
                id: roi_check_box
                checked: manager.roi_indicator
                anchors.centerIn: parent
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 2
            Text {
                anchors.centerIn: parent
                text: "Получить маски деталей"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            CheckBox {
                id: mask_check_box
                checked: manager.mask_indicator
                anchors.centerIn: parent
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 2
            Text {
                anchors.centerIn: parent
                text: "Получить маски рук"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            CheckBox {
                id: hand_check_box
                checked: manager.hand_indicator
                anchors.centerIn: parent
            }
        }
    }
    FolderDialog {
        id: fileDialog
        onAccepted: {
            console.log("dir: " + fileDialog.fileUrls);
        }
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
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: step2dir.gotoMainView()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: {
            manager.raw_photos_path = raw_photos_text_field.text
            manager.processed_path = processed_text_field.text
            manager.roi_indicator = roi_check_box.checkState
            manager.mask_indicator = mask_check_box.checkState
            manager.hand_indicator = hand_check_box.checkState

            step2dir.gotoThreshold()
        }
    }
}
