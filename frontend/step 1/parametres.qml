import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Qt.labs.platform
import QtQml
Item {
    id: parametres
    signal gotoMainView()
    signal gotoCamera()
    signal gotoStep1()

    
        GridLayout {
        id: layout
        anchors.centerIn: parent
        rows: 7
        columns: 3
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Определите параметры для фотосъёмки деталей"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 270
            Layout.preferredHeight: 20
            Layout.columnSpan: 2

            Text {
                x: 5
                text: "Статическая разметка"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            CheckBox {
                id: static_check
                checked: manager.static_indicator
                anchors.centerIn: parent
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Папка для сохранения исходных фото деталей"
            }
        }
        TextField {
            id: raw_photos_path
            Layout.columnSpan: 2
            Layout.minimumWidth: 270
            // Layout.maximumWidth: 670
            text: manager.raw_photos_path
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
                text: "Количество фотографий на одну деталь"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            Layout.columnSpan: 3
            // Layout.minimumWidth: 270
            Layout.alignment: Qt.AlignHCenter
            // Layout.minimumWidth: parent
            TextField {
                anchors.centerIn: parent
                validator: IntValidator {
                    bottom: 1;
                }
                text: manager.snapshots_number
                horizontalAlignment: TextInput.AlignHCenter
                // anchors.fill: parent


                
                onTextEdited: {
                    manager.photo_num = text
                    console.log("photo num = " + text)
                }
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 3
            Text {
                anchors.centerIn: parent
                text: "Пауза между кадрами"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            Layout.columnSpan: 3
            // Layout.minimumWidth: 270
            Layout.alignment: Qt.AlignHCenter
            // Layout.minimumWidth: parent
            TextField {
                id: pause
                text: manager.iou
                horizontalAlignment: TextInput.AlignHCenter
                validator: DoubleValidator {
                    bottom: 0.0;
                    top: 1.0;
                    notation: DoubleValidator.ScientificNotation;
                }
                anchors.centerIn: parent
                property string previousText: ""
                onTextEdited: {
                    var numericValue = getValue()
                    if (numericValue >= 1.0 || numericValue < 0.0)
                    {
                        text = previousText
                        console.log("numericValue = ", numericValue)
                    }
                    previousText = text
                    var numericValue = getValue()
                    // text = Number(previousText)
                    manager.iou = text // Number(previousText)
                    console.log("iou = " + text)
                }
                function setValue(_value)
                {
                    text = String(_value)
                }

                function getValue()
                {
                    return Number(text)
                }
            }
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
    Button {
        id: button2
        text: qsTr("Назад")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        onClicked: parametres.gotoStep1()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: {
            manager.raw_photos_path = raw_photos_path.text
            manager.static_indicator = static_check.checkState
            parametres.gotoCamera()
            }
    }
}
