import QtQuick 2.12
import QtQuick.Window 2.12
import QtQuick.Controls 2.0
import QtQuick.Dialogs 1.2
// Попытка сделать главную страницу
/*
1) Изменить кнопку "назад" так, чтобы не открывалось новое окно
2) Добавить скрипт с камерой и соединить его со скриптом про список
*/
import QtQuick.Layouts 1.1
ApplicationWindow {
    width: 640
    height: 480
    visible: true
    title: qsTr("Генерация наборов данных")
    ColumnLayout {
        spacing: 10
        anchors.fill: parent
        anchors.margins: 25
        MyButton {
            id: button1
            text: "Сфотографировать детали"
            onClicked: {
                loader.setSource("step1list.qml")
                button1.visible = false
                button2.visible = false
                button3.visible = false
            }
        }
        MyButton {
            id: button2
            text: "Получить маски деталей"
           // onClicked: {
//                  loader.source = "step1_1.qml"
//
//                button1.visible = false
//                button2.visible = false
//                button3.visible = false
//            }
        }
        MyButton {
            id: button3
            text: "Сгенерировать наборы данных"
//            onClicked: {
//                button1.visible = false
//                button2.visible = false
//                button3.visible = false
//            }
        }
        // Loader для загрузки страниц


    }
    Loader {
        id: loader
        anchors.fill: parent
    }
}
