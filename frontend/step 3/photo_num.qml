import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs
import Qt.labs.platform
import QtQml

Item {
    id: step3photo_num
    signal gotoGeneration()
    signal gotoStep3()
    GridLayout {
        id: layout
        anchors.centerIn: parent
        rows: 6
        columns: 2
        Rectangle {
            color: 'transparent'
            Layout.fillWidth: true
            Layout.preferredHeight: 20
            Layout.columnSpan: 2
            Text {
                anchors.centerIn: parent
                text: "Определите параметры для генерируемого датасета"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 270
            Layout.preferredHeight: 40
            Text {
                x: 5
                text: "Количество изображений"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            TextField {
                id: photo_num_field
                validator: IntValidator {
                    bottom: 1;
                }
                text: manager.photo_num
                anchors.centerIn: parent
                horizontalAlignment: TextInput.AlignHCenter
                onTextEdited: {
                    manager.photo_num = text
                    console.log("photo num = " + text)
                }
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 270
            Layout.preferredHeight: 40
            Text {
                x: 5
                text: "Максимальное количество деталей\nна одном изображении"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            TextField {
                validator: IntValidator {
                    bottom: 1;
                }
                text: manager.max_details_on_photo
                anchors.centerIn: parent
                horizontalAlignment: TextInput.AlignHCenter
                maximumLength: 2
                onTextEdited: {
                    manager.max_details_on_photo = text
                    console.log("max_details_on_photo = " + text)
                }
            }
        }
        Rectangle {
            id: rect3
            color: 'transparent'
            Layout.preferredWidth: 270
            Layout.preferredHeight: 40
            Text {
                x: 5
                text: "Максимальный IoU между\nпересекающимися объектами"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            TextField {
                id: iou_field
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
                    manager.iou = text
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
       
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 270
            Layout.preferredHeight: 40
            Text {
                x: 5
                text: "Наложение деталей на новые фоны\nпо прямоугольным маскам"
            }
        }
        Rectangle {
            color: 'transparent'
            Layout.preferredWidth: 100
            Layout.preferredHeight: 40
            CheckBox {
                id: rectangle_check
                checked: manager.rectangle_indicator
                anchors.centerIn: parent
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
        onClicked: step3photo_num.gotoStep3()
    }
    Button {
        id: button3
        text: qsTr("Вперед")
        width: (parent.width / 6)
        anchors.margins: 20
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        onClicked: { 
            step3photo_num.gotoGeneration(); 
            manager.rectangle_indicator = rectangle_check.checkState != 0 ? 1 : 0;
            manager.photo_num = parseInt(photo_num_field.text);
            manager.iou = parseFloat(iou_field.text);

        }
    }
    Keys.onUpPressed: manager.photo_num++
    Keys.onDownPressed: manager.photo_num--
    Keys.onEnterPressed: step3photo_num.gotoGeneration()
    Keys.onEscapePressed: step3photo_num.gotoBacks()
}
