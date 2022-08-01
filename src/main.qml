import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
/*
Доделать:
1) Перенос клика при создании нового поля (курсор в новом поле для ввода)
2) Удаление элементов (при клике на ячейку нужно присвоить ее номер textIndex-у)
3) Загрузка списка деталей вместо ввода по полям - как аналог ввода

*/
ApplicationWindow {
    visible: true
    width: 640
    height: 480
    title: qsTr("Генерация наборов данных")

    /* Number created buttons for her visual identification of the demonstration project
     */
    property int number: 0

    /* The string field that displays dynamically pressed the button index button
     * to create dynamic buttons, and a button to delete the index of dynamic buttons
     * */
    Row {
        id: row
        // Set line size and nailed to the top of the application window
        height: 50
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right

        Rectangle {
            width: (parent.width / 5)
            height: 50

            // Set the text box to accommodate the key index
            Text {
                id: textIndex
                anchors.fill: parent
                text: ""
                verticalAlignment: Text.AlignVCenter
                horizontalAlignment: Text.AlignHCenter
            }
        }

        // Button to create dynamic buttons
        Button {
            id: button1
            text: qsTr("Add detail")
            width: (parent.width / 5)*2
            height: 50

            /* By clicking on the button to add the model ListView object
             * with the specified parameters
             * */
            onClicked: {
                listModel.append({idshnik: "Button " + (++number)})

            }
        }

        // Button to remove the dynamic buttons
        Button {
            id: button2
            text: qsTr("Delete detail")
            width: (parent.width / 5)*2
            height: 50

            // Remove the button on its index in the ListView
            onClicked: {
                // if(textIndex.text != ""){
                if (number != 0) {
                    listModel.remove(--number)
                    textIndex.text = "" // Null text box with index
                }
            }
        }
    }

    // ListView to represent the data as a list
    ListView {
        id: listView1
        // We place it in the remainder of the application window
        anchors.top: row.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        /* in this property we specify the layout of the object
         * that will be displayed in the list as a list item
         * */
        delegate: Item {
            id: item
            anchors.left: parent.left
            anchors.right: parent.right
            height: 40
            TextField {
                //anchors.horizontalCenter: parent.horizontalCenter
                anchors.fill: parent
                anchors.margins: 3
                height: 20
                Keys.onReturnPressed: {
                    listModel.append({idshnik: "Button " + (++number)})
                    textIndex.text = index

                }

            }
        }

        model: ListModel {
            id: listModel
        }
    }
}
//import QtQuick.Layouts 1.1
//Window {
//    width: 640
//    height: 480
//    visible: true
//    title: qsTr("Генерация наборов данных")
//    ColumnLayout {
//        spacing: 10
//        anchors.fill: parent
//        anchors.margins: 25
//        MyButton {
//            id: button1
//            text: "Сфотографировать детали"
//            onClicked: {
//                 button1.visible = false
//               // anchors.fill = false
//                button2.visible = false
//                button3.visible = false
//                Rectangle {
//                    color: "red"
//                    width: 100
//                    height: 100
//                }
//            }
//        }
//        MyButton {
//            id: button2
//            text: "Получить маски деталей"
//            onClicked: {
//                button1.visible = false
//                button2.visible = false
//                button3.visible = false
//            }
//        }
//        MyButton {
//            id: button3
//            text: "Сгенерировать наборы данных"
//            onClicked: {
//                button1.visible = false
//                button2.visible = false
//                button3.visible = false
//            }
//        }
//    }
//}
