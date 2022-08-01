import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.0
/*
Цель: страница по внесению названий деталей
Сделано: добавляются новые поля ввода при нажатии на кнопку/EnterKey
+ удаляется последнее поле при нажатии на кнопку удаления
Доделать:
1) Перенос клика при создании нового поля (курсор в новом поле для ввода) + перемещение по клавишам "вверх-вниз"
2) Загрузка списка деталей вместо ввода по полям - как аналог ввода
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
        Button {
            id: button0
            text: qsTr("Загрузить список деталей")
            width: (parent.width / 3)
            height: 50
            onClicked: {

            }
        }
        Button {
            id: button1
            text: qsTr("Добавить деталь")
            width: (parent.width / 3)
            height: 50
            onClicked: {
                listModel.append({idshnik: "TextEditor " + (++number)})

            }
        }

        // Button to remove the dynamic texteditors
        Button {
            id: button2
            text: qsTr("Удалить деталь")
            width: (parent.width / 3)
            height: 50

            // Remove the last texteditor
            onClicked: {
                if (number != 0) {
                    listModel.remove(--number)
                    textIndex.text = ""
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
// Попытка сделать главную страницу и от неё топать, но осталась в черновиках
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
